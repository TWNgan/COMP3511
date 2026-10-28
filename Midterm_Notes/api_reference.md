# API Reference — Linux System Calls & Pthreads（Lab / PA 編程題速查）

> Announcement：「There may be questions related to PA or coding questions using some APIs we discussed in our lab classes」→ 呢頁就係用嚟填空 / 寫 code。

---

## 1. Process APIs
| Call | Header | Return | 重點 |
|---|---|---|---|
| `pid_t fork(void)` | `<unistd.h>` | child: **0**；parent: **child PID (>0)**；fail: **−1** | child 由下一句開始；複製 address space（COW） |
| `int execlp(const char *file, const char *arg0, ..., (char *)NULL)` | `<unistd.h>` | **success: no return**；fail: −1 | 用 PATH 搵 program；**arg0 = program name**；最後一定要 `NULL` |
| `int execvp(const char *file, char *const argv[])` | `<unistd.h>` | 同上 | `argv` 最後一個元素要係 **NULL**（PA1：所以 array size 係 9 而唔係 8） |
| `int execl(path, arg0, ..., NULL)` / `execv(path, argv)` | `<unistd.h>` | 同上 | 要 full path（冇 p = 唔搵 PATH） |
| `pid_t wait(int *status)` | `<sys/wait.h>` | terminated child 嘅 PID；冇 child → −1 | `wait(NULL)` 唔要 status；等**任何一個** child |
| `pid_t waitpid(pid_t pid, int *status, int options)` | `<sys/wait.h>` | 該 child PID；error −1 | `waitpid(pid, &status, 0)` 等指定 child；`WNOHANG` 唔 block |
| `void exit(int status)` | `<stdlib.h>` | — | 結束 process，status 經 wait 交畀 parent（`WEXITSTATUS(status)`） |
| `pid_t getpid(void)` / `getppid(void)` | `<unistd.h>` | 自己 / parent PID | |
| `int chdir(const char *path)` | `<unistd.h>` | 0 / −1 | PA1 `cd`（唔可以用 exec 做 cd，因為要改 shell 自己嘅 cwd） |
| `sighandler_t signal(int signum, sighandler_t handler)` | `<signal.h>` | 舊 handler | `signal(SIGINT, handler)`；`SIG_IGN` 忽略；`SIG_DFL` default |
| `int kill(pid_t pid, int sig)` | `<signal.h>` | 0 / −1 | send signal to process |
| `unsigned int sleep(unsigned int s)` | `<unistd.h>` | 剩餘秒數 | 停 s 秒；`usleep` = µs；`nanosleep`（`<time.h>`）更細 |

**exec family（Lab 3）**：六個 — `execl, execlp, execle, execv, execvp, execvpe`；全部 **replace the current process image，成功唔會 return，失敗 −1**。

| 字母 | 意思 | 例 |
|---|---|---|
| **l** (list) | arguments 逐個列出，數目 compile time 已知 | `execlp("ls", "ls", "-l", "-h", NULL);` |
| **v** (vector) | arguments 放喺 array（尾要 NULL）；數目唔知時用 | `char *a[] = {"ls", "-l", NULL}; execvp("ls", a);` |
| **p** (path) | 用 **PATH** 搵 program（唔使 full path） | `execlp` / `execvp` / `execvpe` |
| **e** (env) | 額外傳 environment array | `execle` / `execvpe` |

### 1.1 經典 fork–exec–wait
```c
pid_t pid = fork();
if (pid < 0) { perror("fork"); exit(1); }
else if (pid == 0) {                       /* child */
    execlp("ls", "ls", "-l", (char *)NULL);
    perror("exec failed");                  /* only reached if exec fails */
    exit(1);
} else {                                   /* parent */
    int status;
    waitpid(pid, &status, 0);              /* or wait(NULL) */
}
```

### 1.2 Signal handler（PA1 Feature 2）
```c
void handle_sigint(int signum) {
    printf("Myshell (pid=%d) terminates by Ctrl-C with signal: %d\n", getpid(), signum);
    exit(0);
}
int main() { signal(SIGINT, handle_sigint); /* ... */ }
```
- SIGINT = **2**（Ctrl-C）；SIGKILL (9)、SIGSTOP 唔可以 catch。

---

## 2. File I/O（POSIX，唔係 stdio）
| Call | Return | 重點 |
|---|---|---|
| `int open(const char *path, int flags[, mode_t mode])` `<fcntl.h>` | **lowest unused fd** / −1 | flags：`O_RDONLY`、`O_WRONLY`、`O_RDWR`、`O_CREAT`、`O_TRUNC`、`O_APPEND`；建立檔案要 mode（e.g. `0644`） |
| `ssize_t read(int fd, void *buf, size_t count)` | bytes read；**0 = EOF**；−1 error | blocking（pipe 冇 data 會等；所有 write ends close 晒先 return 0） |
| `ssize_t write(int fd, const void *buf, size_t count)` | bytes written / −1 | |
| `int close(int fd)` | 0 / −1 | **用完要 close**，尤其 pipe write end |
| `int dup(int oldfd)` | 新 fd = **lowest unused** | `close(0); dup(fin);` → fd 0 指向 file |
| `int dup2(int oldfd, int newfd)` | newfd | newfd 已開 → 先 close；`dup2(fd, 1)` = stdout 指向 fd |

- **fd 0 = stdin，1 = stdout，2 = stderr**（`STDIN_FILENO`, `STDOUT_FILENO`, `STDERR_FILENO`）。
- Lab 3 permission 寫法：`open("hello.txt", O_CREAT | O_WRONLY, S_IRUSR | S_IWUSR)`（**600**：owner read + write）；`O_RDONLY` 開讀。
- ⚠️ **唔好用 stdio 嘅 `fopen/fread/fwrite/fclose`（`FILE*`）做 PA**：`FILE*` 係 C library struct，**cannot be used in pipe operations**。
- **Output redirection**（`cmd > out.txt`）：
```c
int fout = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
dup2(fout, STDOUT_FILENO);  close(fout);   /* then exec */
```
- **Input redirection**（`cmd < in.txt`）：
```c
int fin = open("in.txt", O_RDONLY);
dup2(fin, STDIN_FILENO);  close(fin);      /* or: close(0); dup(fin); */
```

---

## 3. Pipes
| Call | 重點 |
|---|---|
| `int pipe(int fd[2])` `<unistd.h>` | **fd[0] = read end，fd[1] = write end**；0 / −1；**一定喺 fork() 之前 call** |
| `int mkfifo(const char *path, mode_t mode)` `<sys/stat.h>` | named pipe（FIFO），之後用 `open()`/`read()`/`write()`；要 `unlink()` 刪除；0 / −1 |
| `int access(const char *path, int how)` `<unistd.h>` | `F_OK` 存在、`R_OK`/`W_OK`/`X_OK` 權限；0 = OK，−1 = 唔得（Lab 4：`if (access(FIFO, F_OK) == -1) mkfifo(FIFO, 0777);`） |
| `FILE *popen(const char *cmd, const char *type)` / `int pclose(FILE *fp)` `<stdio.h>` | fork 一個 child 跑 cmd；`"r"` 讀佢 stdout、`"w"` 寫佢 stdin；`pclose` 等佢完返回 status（**PA1 禁用**） |

- **FIFO 特性（Lab 4）**：`open/read/write` **blocking**，**要兩端都有 process open 先繼續**（可用 `O_NONBLOCK`）；data **讀咗就冇**（唔可以 broadcast）；**≤ `PIPE_BUF` bytes 嘅 write 係 atomic**；一條 FIFO 實際唔適合雙向（可能讀返自己寫嘅）→ 雙向用兩條。
- **兩條 ordinary pipes 做雙向**：`pipe(p2c); pipe(c2p);` → child：`close(c2p[0]); write(c2p[1], …); close(p2c[1]); read(p2c[0], …);`；parent：`close(c2p[1]); read(c2p[0], …); close(p2c[0]); write(p2c[1], …);`（Lab 4 exam example）。

### 3.1 Parent → child
```c
int fd[2]; pipe(fd);
if (fork() == 0) {               /* child: reader */
    close(fd[1]);
    int n; read(fd[0], &n, sizeof(n));
    close(fd[0]); exit(0);
} else {                         /* parent: writer */
    close(fd[0]);
    int n = 6; write(fd[1], &n, sizeof(n));
    close(fd[1]); wait(NULL);
}
```

### 3.2 Shell pipeline `ls | wc -l`
```c
int fd[2]; pipe(fd);
if (fork() == 0) {               /* child 1: ls → pipe */
    dup2(fd[1], STDOUT_FILENO);
    close(fd[0]); close(fd[1]);
    execlp("ls", "ls", (char *)NULL);
}
if (fork() == 0) {               /* child 2: pipe → wc */
    dup2(fd[0], STDIN_FILENO);
    close(fd[0]); close(fd[1]);
    execlp("wc", "wc", "-l", (char *)NULL);
}
close(fd[0]); close(fd[1]);      /* parent MUST close both, else wc never sees EOF */
wait(NULL); wait(NULL);
```
- **Multi-level pipe（PA1 Feature 5）**：n segments → n−1 pipes；segment i：`dup2(fds[i-1][0], 0)`（if i > 0）、`dup2(fds[i][1], 1)`（if i < n−1）；每個 child close 所有 pipe fds；parent close 所有 fds 再 wait 全部。

### 3.3 常見錯誤
1. `pipe()` 喺 `fork()` 之後 call → 兩條唔相關嘅 pipe（HW1 Q3.3c）。
2. 冇 close 未用嘅 write end → reader `read()` 永遠唔會得到 EOF（hang）。
3. `write(fd[0], …)` / `read(fd[1], …)` 搞錯方向（**0 讀 1 寫**：記「0 = stdin-like，1 = stdout-like」）。
4. `read`/`write` 第二個參數要 **address**（`&cnt`），第三個係 **size**（`sizeof(int)`）。

---

## 4. Pthreads（`#include <pthread.h>`，compile with `-pthread`）
| Call | 重點 |
|---|---|
| `int pthread_create(pthread_t *tid, const pthread_attr_t *attr, void *(*start)(void *), void *arg)` | return 0 = success；attr 用 `NULL`；start routine signature `void *f(void *)` |
| `int pthread_join(pthread_t tid, void **retval)` | 等 thread 結束（類似 wait）；`retval` 可 NULL |
| `void pthread_exit(void *retval)` | thread 自己結束 |
| `int pthread_cancel(pthread_t tid)` | request cancellation（default **deferred**） |
| `pthread_t pthread_self(void)` | 自己 tid |
| `int pthread_kill(pthread_t tid, int sig)` | signal 指定 thread |
| `int pthread_attr_init(pthread_attr_t *attr)` | default attributes（stack size, scheduling info）→ 再傳畀 `pthread_create`（Lab 4 sum example） |
| `pthread_cond_broadcast(&cond)` | 叫醒**所有**等緊嘅 threads（`pthread_cond_signal` 只叫醒一個） |

```c
void *worker(void *arg) { int id = *(int *)arg; printf("thread %d\n", id); return NULL; }
int main() {
    pthread_t t[3]; int id[3];
    for (int i = 0; i < 3; i++) { id[i] = i; pthread_create(&t[i], NULL, worker, &id[i]); }
    for (int i = 0; i < 3; i++) pthread_join(t[i], NULL);
    return 0;
}
```

### 4.1 Mutex
```c
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;   /* or pthread_mutex_init(&m, NULL) */
pthread_mutex_lock(&m);   /* critical section */   pthread_mutex_unlock(&m);
pthread_mutex_destroy(&m);
```

### 4.2 POSIX unnamed semaphore（`#include <semaphore.h>`）
```c
sem_t s;
sem_init(&s, 0, 1);    /* pshared = 0 → shared between threads of this process; initial value 1 */
sem_wait(&s);          /* P(): if value > 0 decrement, else block */
sem_post(&s);          /* V(): increment, wake a waiter */
sem_destroy(&s);
```
- **Ordering**：`sem_init(&s, 0, 0)`；先做嘅 thread 做完 `sem_post(&s)`，後做嘅 thread 開頭 `sem_wait(&s)`。
- **Mutual exclusion**：init 1；`sem_wait` → CS → `sem_post`。
- **Counting resources**：init = 資源數量 n。

### 4.3 Condition variables
```c
pthread_mutex_t m; pthread_cond_t c; int ready = 0;
/* waiter */
pthread_mutex_lock(&m);
while (!ready) pthread_cond_wait(&c, &m);   /* releases m while sleeping, re-acquires on wake */
pthread_mutex_unlock(&m);
/* signaller */
pthread_mutex_lock(&m); ready = 1; pthread_cond_signal(&c); pthread_mutex_unlock(&m);
```
- 一定要持有 mutex 先 call；用 **while**（唔係 if）再 check 條件。

---

## 5. Compile / Run（Lab 1–2）
```bash
gcc -pedantic -Wall -Wextra -std=c99 -o myshell myshell.c
gcc prog.c -o prog -lpthread       # pthread programs (or -pthread)
gcc buggy.c -o buggy -g            # debug info, then: gdb buggy
./mlfq < input.txt > output.txt    # PA2: input/output redirection
diff --side-by-side my-out.txt sample-out.txt   # compare outputs (--suppress-common-lines)
gcc main.c -o main -lm             # link math library (linker!)
./prog
```
- `gcc -c main.c` → `main.o`（compiler）；`gcc -o main main.o -lm`（linker）；`./main`（loader）[2.32]。
