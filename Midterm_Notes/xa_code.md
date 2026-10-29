# Copy-ready C programs（Lab / PA API coding questions）

## [XC-01] ch3 | fork + wait + exit status
Write a program in which the child prints its own PID and its parent's PID, and the parent waits for the child and prints the child's exit status.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid = fork();
    if (pid < 0) {                          /* fork failed */
        perror("fork");
        exit(1);
    } else if (pid == 0) {                  /* child: fork() returned 0 */
        printf("child: pid=%d parent=%d\n", getpid(), getppid());
        exit(7);                            /* status passed to the parent */
    } else {                                /* parent: fork() returned the child's PID */
        int status;
        waitpid(pid, &status, 0);           /* or wait(&status) */
        if (WIFEXITED(status))
            printf("parent: child %d exited with %d\n", pid, WEXITSTATUS(status));
    }
    return 0;
}
```
- Parent output is always after the child's (it **waits**). Without `wait`, the finished child stays a **zombie** until reaped.

## [XC-02] ch3 | N children (fan) + reap all
The parent creates N child processes; child i prints i and terminates; the parent waits for all children before printing "done".

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#define N 4

int main(void) {
    for (int i = 0; i < N; i++) {
        pid_t pid = fork();
        if (pid == 0) {                     /* child i */
            printf("child %d: pid=%d\n", i, getpid());
            exit(0);                        /* MUST exit: otherwise the child continues the loop and forks too */
        }
    }
    while (wait(NULL) > 0)                  /* reap every child (no zombies); wait returns -1 when none left */
        ;
    printf("parent: done\n");
    return 0;
}
```
- Exactly **N + 1** processes. Children print in **any order** (scheduler decides); "done" is always last.

## [XC-03] ch3 | Chain of processes
Create a chain P0 → P1 → … → PN in which each process creates exactly one child and waits for it.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#define N 3

int main(void) {
    for (int i = 0; i < N; i++) {
        pid_t pid = fork();
        if (pid > 0) {                      /* parent: wait for its only child, then stop forking */
            wait(NULL);
            break;
        }                                   /* child: continue the loop and create the next process */
    }
    printf("pid=%d parent=%d\n", getpid(), getppid());
    return 0;
}
```
- **N + 1** processes; the deepest prints first, each parent prints after its child ends (reverse order of creation).

## [XC-04] ch3 | fork + execvp a command line
The parent reads a command line (e.g. "ls -l -a"), runs it in a child with `execvp`, and waits for it.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    char line[] = "ls -l -a";
    char *argv[9];                          /* at most 8 arguments + NULL terminator */
    int argc = 0;
    for (char *tok = strtok(line, " "); tok != NULL && argc < 8; tok = strtok(NULL, " "))
        argv[argc++] = tok;
    argv[argc] = NULL;                      /* execvp needs a NULL-terminated array */

    pid_t pid = fork();
    if (pid == 0) {
        execvp(argv[0], argv);              /* replaces the child's image; returns only on error */
        perror("execvp");
        exit(1);
    }
    waitpid(pid, NULL, 0);
    printf("command finished\n");
    return 0;
}
```
- Code after a **successful exec never runs** (the process image is replaced; PID stays the same).
- `execlp("ls", "ls", "-l", "-a", (char *)NULL)` is the list form of the same call.

## [XC-05] ch3 | Pipe: parent sends a string to child
Use an ordinary pipe so that the parent sends the string "Greetings" to the child, which prints it.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    int fd[2];                              /* fd[0] = read end, fd[1] = write end */
    char buf[100];
    if (pipe(fd) == -1) { perror("pipe"); exit(1); }   /* create BEFORE fork so both share it */
    pid_t pid = fork();
    if (pid == 0) {                         /* child = reader */
        close(fd[1]);                       /* close unused write end */
        ssize_t n = read(fd[0], buf, sizeof(buf) - 1);
        buf[n > 0 ? n : 0] = '\0';
        printf("child read: %s\n", buf);
        close(fd[0]);
        exit(0);
    } else {                                /* parent = writer */
        close(fd[0]);                       /* close unused read end */
        const char *msg = "Greetings";
        write(fd[1], msg, strlen(msg));
        close(fd[1]);                       /* signals EOF to the reader */
        wait(NULL);
    }
    return 0;
}
```

## [XC-06] ch3 | Pipe: child computes, parent receives
The child computes 1 + 2 + … + 100 and sends the result to the parent through a pipe; the parent prints it.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    int fd[2];
    pipe(fd);
    if (fork() == 0) {                      /* child: writer */
        close(fd[0]);
        int sum = 0;
        for (int i = 1; i <= 100; i++) sum += i;
        write(fd[1], &sum, sizeof(sum));    /* pass the ADDRESS and the SIZE */
        close(fd[1]);
        exit(0);
    }
    close(fd[1]);                           /* parent: reader */
    int result;
    read(fd[0], &result, sizeof(result));   /* blocks until data arrives */
    close(fd[0]);
    wait(NULL);
    printf("sum = %d\n", result);           /* 5050 */
    return 0;
}
```
- A global variable changed in the child is **not** seen by the parent (separate address spaces). That's why IPC (a pipe) is needed.

## [XC-07] ch3 | Two pipes: two-way communication
Parent sends "Parent" to the child and the child replies "Child", using two ordinary pipes.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    int p2c[2], c2p[2];                     /* parent->child, child->parent */
    char buf[20] = {0};
    pipe(p2c);
    pipe(c2p);
    if (fork() == 0) {                      /* child */
        close(p2c[1]); close(c2p[0]);       /* keep: read p2c, write c2p */
        read(p2c[0], buf, sizeof(buf) - 1);
        printf("child received: %s\n", buf);
        write(c2p[1], "Child", 6);          /* 6 bytes include the '\0' */
        close(p2c[0]); close(c2p[1]);
        exit(0);
    }
    close(p2c[0]); close(c2p[1]);           /* parent keeps: write p2c, read c2p */
    write(p2c[1], "Parent", 7);
    read(c2p[0], buf, sizeof(buf) - 1);
    printf("parent received: %s\n", buf);
    close(p2c[1]); close(c2p[0]);
    wait(NULL);
    return 0;
}
```
- One ordinary pipe is **unidirectional** → two-way needs **two pipes** (a single pipe could read back its own message).

## [XC-08] ch3 | Redirection: cmd < in > out
Implement `sort < in.txt > out.txt`: run `sort` in a child with stdin from in.txt and stdout to out.txt.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    if (fork() == 0) {
        int in  = open("in.txt", O_RDONLY);
        int out = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);   /* 0644: rw-r--r-- */
        if (in < 0 || out < 0) { perror("open"); exit(1); }
        dup2(in, STDIN_FILENO);             /* fd 0 now refers to in.txt   */
        dup2(out, STDOUT_FILENO);           /* fd 1 now refers to out.txt  */
        close(in); close(out);              /* originals no longer needed  */
        execlp("sort", "sort", (char *)NULL);
        perror("execlp");
        exit(1);
    }
    wait(NULL);
    return 0;
}
```
- Equivalent old style: `close(1); dup(out);` (dup returns the **lowest unused fd** = 1). Redirect **in the child, before exec**; the shell's own stdin/stdout stay unchanged.

## [XC-09] ch3 | Pipeline: ls | wc -l
Implement the shell command `ls | wc -l` with `pipe`, `fork`, `dup2` and `exec`.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    int fd[2];
    pipe(fd);
    if (fork() == 0) {                      /* child 1: ls writes into the pipe */
        dup2(fd[1], STDOUT_FILENO);
        close(fd[0]); close(fd[1]);
        execlp("ls", "ls", (char *)NULL);
        exit(1);
    }
    if (fork() == 0) {                      /* child 2: wc reads from the pipe */
        dup2(fd[0], STDIN_FILENO);
        close(fd[0]); close(fd[1]);
        execlp("wc", "wc", "-l", (char *)NULL);
        exit(1);
    }
    close(fd[0]); close(fd[1]);             /* parent MUST close both ends, else wc never sees EOF */
    wait(NULL);
    wait(NULL);
    return 0;
}
```
- Every process **closes the pipe ends it does not use**; an open write end anywhere keeps the reader blocked (no EOF).

## [XC-10] ch3 | Multi-level pipe (PA1 Feature 5)
Write `run_pipeline(cmds, n)` that runs `cmd0 | cmd1 | … | cmd(n-1)` (n ≤ 8), where `cmds[i]` is a NULL-terminated argv array.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

void run_pipeline(char **cmds[], int n) {
    int fds[8][2];                          /* n-1 pipes */
    for (int i = 0; i < n - 1; i++) pipe(fds[i]);
    for (int i = 0; i < n; i++) {
        if (fork() == 0) {
            if (i > 0)     dup2(fds[i - 1][0], STDIN_FILENO);   /* read the previous pipe */
            if (i < n - 1) dup2(fds[i][1], STDOUT_FILENO);      /* write the next pipe   */
            for (int k = 0; k < n - 1; k++) { close(fds[k][0]); close(fds[k][1]); }
            execvp(cmds[i][0], cmds[i]);
            perror("execvp");
            exit(1);
        }
    }
    for (int k = 0; k < n - 1; k++) { close(fds[k][0]); close(fds[k][1]); }   /* parent closes all */
    for (int i = 0; i < n; i++) wait(NULL);                                   /* then waits for all */
}

int main(void) {
    char *c0[] = {"printf", "b\\na\\nc\\n", NULL};
    char *c1[] = {"sort", NULL};
    char *c2[] = {"head", "-n", "2", NULL};
    char **cmds[] = {c0, c1, c2};
    run_pipeline(cmds, 3);                  /* prints a, b */
    return 0;
}
```
- n segments → **n − 1 pipes** and **n children**; the first child keeps its stdin, the last keeps its stdout.

## [XC-11] ch3 | Mini shell loop: built-in cd, exit, Ctrl-C
Sketch the main loop of a simple shell (PA1): prompt, read a line, handle `exit` and `cd` as built-ins, run other commands in a child, and print a message on Ctrl-C.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>

void on_sigint(int sig) {                   /* SIGINT = 2 */
    printf("\nshell (pid=%d) terminated by Ctrl-C, signal %d\n", getpid(), sig);
    exit(0);
}

int main(void) {
    char line[1024], *argv[9];
    signal(SIGINT, on_sigint);              /* register the handler */
    while (1) {
        printf("$$ 3511> ");
        fflush(stdout);
        if (fgets(line, sizeof(line), stdin) == NULL) break;   /* EOF */
        line[strcspn(line, "\n")] = '\0';
        int argc = 0;
        for (char *t = strtok(line, " "); t != NULL && argc < 8; t = strtok(NULL, " "))
            argv[argc++] = t;
        argv[argc] = NULL;
        if (argc == 0) continue;
        if (strcmp(argv[0], "exit") == 0) break;
        if (strcmp(argv[0], "cd") == 0) {   /* built-in: must change the SHELL's own directory */
            if (argc < 2 || chdir(argv[1]) != 0) perror("cd");
            continue;
        }
        pid_t pid = fork();
        if (pid == 0) {
            execvp(argv[0], argv);
            perror("execvp");
            exit(1);
        }
        waitpid(pid, NULL, 0);              /* foreground: wait before the next prompt */
    }
    return 0;
}
```
- `cd` in a child would change only the **child's** working directory, which disappears when the child exits. So it must be built in, using `chdir()`.
- `system()` / `popen()` are not allowed (they start another shell to do the work).

## [XC-12] ch3 | Named pipe (FIFO) writer / reader
Two unrelated processes communicate through a named pipe "/tmp/myfifo": the writer sends a string, the reader prints it.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#define FIFO "/tmp/myfifo"

void writer(void) {                         /* program 1 */
    int fd = open(FIFO, O_WRONLY);          /* blocks until a reader opens the FIFO */
    const char *msg = "hello via FIFO";
    write(fd, msg, strlen(msg) + 1);
    close(fd);
}

void reader(void) {                         /* program 2 */
    char buf[100];
    int fd = open(FIFO, O_RDONLY);          /* blocks until a writer opens the FIFO */
    read(fd, buf, sizeof(buf));
    printf("reader got: %s\n", buf);
    close(fd);
}

int main(void) {                            /* demo in one file; normally two separate programs */
    if (access(FIFO, F_OK) == -1) mkfifo(FIFO, 0666);   /* create the FIFO file once */
    if (fork() == 0) { writer(); exit(0); }
    reader();
    wait(NULL);
    unlink(FIFO);                           /* remove the FIFO when finished */
    return 0;
}
```
- A FIFO **appears as a file** in the file system, needs **no parent–child relationship**, and **exists until deleted** (`unlink`). An ordinary pipe exists only while its processes use it.

## [XC-13] ch4 | Pthreads: partial sums with N threads
Use N threads to sum an array: thread i sums its own slice, and `main` joins all threads and adds the partial sums.

**Answer:**
```c
#include <stdio.h>
#include <pthread.h>
#define N 4
#define SIZE 1000

int a[SIZE];
long partial[N];                            /* one slot per thread → no shared write → no race */

void *worker(void *arg) {
    int id = *(int *)arg;
    long s = 0;
    for (int i = id * (SIZE / N); i < (id + 1) * (SIZE / N); i++) s += a[i];
    partial[id] = s;
    return NULL;                            /* or pthread_exit(NULL) */
}

int main(void) {
    pthread_t tid[N];
    int ids[N];
    for (int i = 0; i < SIZE; i++) a[i] = i + 1;
    for (int i = 0; i < N; i++) {
        ids[i] = i;                         /* pass &ids[i], NOT &i (i changes while threads start) */
        pthread_create(&tid[i], NULL, worker, &ids[i]);
    }
    long total = 0;
    for (int i = 0; i < N; i++) {
        pthread_join(tid[i], NULL);         /* wait for thread i */
        total += partial[i];
    }
    printf("total = %ld\n", total);         /* 500500 */
    return 0;
}
```
- Compile: `gcc sum.c -o sum -pthread` (or `-lpthread`). Signature of a thread function: `void *f(void *arg)`.

## [XC-14] ch4 | Thread returns a value to main
Create a thread that computes the square of a number passed as its argument and returns the result to `main` through `pthread_join`.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void *square(void *arg) {
    int x = *(int *)arg;
    int *res = malloc(sizeof(int));         /* heap: survives after the thread ends (not a local!) */
    *res = x * x;
    pthread_exit(res);                      /* same as: return res; */
}

int main(void) {
    pthread_t t;
    int x = 7;
    int *res;
    pthread_create(&t, NULL, square, &x);
    pthread_join(t, (void **)&res);         /* receives the thread's return value */
    printf("%d squared = %d\n", x, *res);  /* 49 */
    free(res);
    return 0;
}
```

## [XC-15] ch6 | Mutex-protected shared counter
Two threads each increment a shared counter 100000 times. Make the final value always 200000.

**Answer:**
```c
#include <stdio.h>
#include <pthread.h>

int counter = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;   /* or pthread_mutex_init(&lock, NULL) */

void *add(void *arg) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);          /* entry section */
        counter++;                          /* critical section */
        pthread_mutex_unlock(&lock);        /* exit section */
    }
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add, NULL);
    pthread_create(&t2, NULL, add, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("counter = %d\n", counter);      /* always 200000 */
    pthread_mutex_destroy(&lock);
    return 0;
}
```
- Without the mutex, `counter++` (load, add, store) **races**, so the result can be anything from 2 to 200000; in practice it is usually less than 200000.

## [XC-16] ch6 | Semaphores: force the order T1 → T2 → T3
Three threads each print their name. Use POSIX semaphores so the output is always T1, T2, T3.

**Answer:**
```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>

sem_t s12, s23;                             /* both start at 0 = "not yet allowed" */

void *t1(void *a) { printf("T1\n"); sem_post(&s12); return NULL; }
void *t2(void *a) { sem_wait(&s12); printf("T2\n"); sem_post(&s23); return NULL; }
void *t3(void *a) { sem_wait(&s23); printf("T3\n"); return NULL; }

int main(void) {
    pthread_t a, b, c;
    sem_init(&s12, 0, 0);                   /* pshared = 0: shared by threads of this process */
    sem_init(&s23, 0, 0);
    pthread_create(&c, NULL, t3, NULL);     /* creation order does not matter */
    pthread_create(&b, NULL, t2, NULL);
    pthread_create(&a, NULL, t1, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL); pthread_join(c, NULL);
    sem_destroy(&s12); sem_destroy(&s23);
    return 0;
}
```
- Rule: for "A before B", use a semaphore initialised to **0**; **A signals (`sem_post`) after its work; B waits (`sem_wait`) before its work.**

## [XC-17] ch6 | Bounded buffer (producer–consumer) with semaphores
Implement a producer and a consumer sharing a bounded buffer of size 5, using `empty`/`full` counting semaphores and a mutex.

**Answer:**
```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#define BUF 5
#define ITEMS 20

int buffer[BUF], in = 0, out = 0;
sem_t empty, full;                          /* empty = free slots (init BUF), full = items (init 0) */
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *producer(void *arg) {
    for (int i = 1; i <= ITEMS; i++) {
        sem_wait(&empty);                   /* wait for a free slot   */
        pthread_mutex_lock(&mutex);
        buffer[in] = i;
        in = (in + 1) % BUF;
        pthread_mutex_unlock(&mutex);
        sem_post(&full);                    /* one more item          */
    }
    return NULL;
}

void *consumer(void *arg) {
    int sum = 0;
    for (int i = 1; i <= ITEMS; i++) {
        sem_wait(&full);                    /* wait for an item       */
        pthread_mutex_lock(&mutex);
        int item = buffer[out];
        out = (out + 1) % BUF;
        pthread_mutex_unlock(&mutex);
        sem_post(&empty);                   /* one more free slot     */
        sum += item;
    }
    printf("consumed sum = %d\n", sum);     /* 210 */
    return NULL;
}

int main(void) {
    pthread_t p, c;
    sem_init(&empty, 0, BUF);
    sem_init(&full, 0, 0);
    pthread_create(&p, NULL, producer, NULL);
    pthread_create(&c, NULL, consumer, NULL);
    pthread_join(p, NULL);
    pthread_join(c, NULL);
    sem_destroy(&empty); sem_destroy(&full);
    return 0;
}
```
- **Order matters:** `wait(empty)` / `wait(full)` must come **before** locking the mutex. Locking first can **deadlock** (holding the mutex while blocked on a full/empty buffer).

## [XC-18] ch6 | First readers–writers (semaphores)
Give a solution where many readers may read together but a writer needs exclusive access (readers have priority).

**Answer:**
```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>

sem_t rw_mutex;                             /* init 1: writers' exclusive access / held by the reader group */
sem_t mutex;                                /* init 1: protects read_count */
int read_count = 0, data = 0;

void *writer(void *arg) {
    sem_wait(&rw_mutex);
    data++;                                 /* writing */
    sem_post(&rw_mutex);
    return NULL;
}

void *reader(void *arg) {
    sem_wait(&mutex);
    read_count++;
    if (read_count == 1) sem_wait(&rw_mutex);   /* first reader locks out writers */
    sem_post(&mutex);

    printf("read %d\n", data);              /* reading (many readers at once) */

    sem_wait(&mutex);
    read_count--;
    if (read_count == 0) sem_post(&rw_mutex);   /* last reader lets writers in */
    sem_post(&mutex);
    return NULL;
}

int main(void) {
    pthread_t r[3], w;
    sem_init(&rw_mutex, 0, 1);
    sem_init(&mutex, 0, 1);
    pthread_create(&w, NULL, writer, NULL);
    for (int i = 0; i < 3; i++) pthread_create(&r[i], NULL, reader, NULL);
    pthread_join(w, NULL);
    for (int i = 0; i < 3; i++) pthread_join(r[i], NULL);
    return 0;
}
```
- Writers may **starve** (readers keep arriving). Lab 6 wrote the same logic with two `pthread_mutex_t` (`mutex`, `rw_mutex`).

## [XC-19] ch3 | Zombie and orphan demos
Write short programs that create (a) a zombie process and (b) an orphan process, and explain what happens.

**Answer:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    /* (a) zombie: child exits, parent is alive but has not called wait() */
    if (fork() == 0) exit(0);
    sleep(1);                               /* during this time the child is a zombie (ps shows <defunct>) */

    /* (b) orphan: parent exits first, child is still running */
    if (fork() == 0) {
        sleep(2);
        printf("orphan: my parent is now %d\n", getppid());   /* re-parented to init / systemd (or a subreaper) */
        exit(0);
    }
    return 0;                               /* parent ends; the zombie from (a) is reaped by init */
}
```
- **Zombie** = terminated, but its PCB / exit status is kept until the parent calls `wait()`. **Orphan** = parent ended without waiting, so **init (systemd) adopts it** and reaps it.
