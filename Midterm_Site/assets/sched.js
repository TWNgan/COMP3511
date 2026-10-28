/*!
 * sched.js - CPU-scheduling simulator for COMP3511 (HKUST) midterm revision.
 * Pure logic, no DOM.  Browser: window.Sched     Node: require('./sched.js')
 *
 * Port of _work/midterm/scripts/sched.py (checked against official exam
 * answers) plus: SRTF tie option, Priority+RR, optional MLFQ aging, RM/EDF tie
 * option, course + textbook response times and a step-by-step event log.
 *
 * Time is discrete: the simulator advances one integer unit per tick and makes
 * every scheduling decision at integer boundaries. Processes are named P1, P2...
 * in input order; "lower id" means the smaller number.
 */
(function () {
  'use strict';

  /* ================================================================ helpers */

  /** Round to dp decimals (default 2) and drop trailing zeros: 23.333 -> "23.33". */
  function fmt(x, dp) {
    if (x === null || x === undefined || !isFinite(x)) return '-';
    var f = Math.pow(10, dp === undefined ? 2 : dp);
    var r = Math.round(x * f + (x >= 0 ? 1e-7 : -1e-7)) / f;
    return String(r === 0 ? 0 : r);
  }

  function blk(start, end, name, level) {
    var lv = level === undefined ? null : level;
    return { start: start, end: end, name: name, level: lv,
      label: lv === null ? name : name + '@Q' + lv };
  }

  /** Merge back-to-back blocks that carry the same label (sched.py merge()). */
  function merge(blocks) {
    var out = [];
    blocks.forEach(function (b) {
      var last = out[out.length - 1];
      if (last && last.label === b.label && last.end === b.start) last.end = b.end;
      else out.push({ start: b.start, end: b.end, name: b.name, level: b.level, label: b.label });
    });
    return out;
  }

  /** "0 P1 4 P2 8 ..." - a start time is repeated only after a gap. */
  function ganttString(blocks) {
    var parts = [], t = null;
    blocks.forEach(function (b) {
      if (t === null || b.start !== t) parts.push(String(b.start));
      parts.push(b.label, String(b.end));
      t = b.end;
    });
    return parts.join(' ');
  }

  function setOnce(obj, k, v) { if (!(k in obj)) obj[k] = v; }

  function lexLess(a, b) {
    for (var i = 0; i < a.length; i++) {
      if (a[i] < b[i]) return true;
      if (a[i] > b[i]) return false;
    }
    return false;
  }

  /** First item with the lexicographically smallest key (like Python's min). */
  function argmin(items, keyFn) {
    var best = null, bk = null;
    items.forEach(function (it) {
      var k = keyFn(it);
      if (best === null || lexLess(k, bk)) { best = it; bk = k; }
    });
    return best;
  }

  function byArrival(a, b) { return a.arrival - b.arrival || a.id - b.id; }
  function names(list) { return list.map(function (p) { return p.name; }).join(', '); }
  function fmtQ(list, lab) { return list.length ? '[' + list.map(lab).join(', ') + ']' : '[ ]'; }
  function units(n) { return n + (n === 1 ? ' unit' : ' units'); }
  function entry(t, events, cpu, why, queue) {
    return { t: t, events: events, cpu: cpu, why: why || '', queue: queue || '' };
  }
  function round9(x) { return Math.round(x * 1e9) / 1e9; }
  function remMap(P) { var r = {}; P.forEach(function (p) { r[p.name] = p.burst; }); return r; }
  function anyLeft(P, rem) { return P.some(function (p) { return rem[p.name] > 0; }); }

  /* ------------------------------------------------------------ validation */

  var MAX_TIME = 20000;

  function toNum(v) {
    if (v === null || v === undefined) return NaN;
    if (typeof v === 'string') return v.trim() === '' ? NaN : Number(v.trim().replace(/\u2212/g, '-'));
    return Number(v);
  }
  function needInt(v, min, what) {
    var n = toNum(v);
    if (!Number.isInteger(n)) throw new Error(what + ' must be a whole number');
    if (min !== null && min !== undefined && n < min) throw new Error(what + ' must be at least ' + min);
    return n;
  }
  function needNum(v, what) {
    var n = toNum(v);
    if (!isFinite(n)) throw new Error(what + ' must be a number');
    return n;
  }
  function blank(v) { return v === undefined || v === null || v === ''; }

  /** [{arrival, burst, priority}] or [[arrival, burst, priority?]] -> normalised list. */
  function normProcs(list, needPriority) {
    if (!Array.isArray(list) || list.length === 0) throw new Error('Add at least one process');
    var P = list.map(function (p, i) {
      var o = Array.isArray(p) ? { arrival: p[0], burst: p[1], priority: p[2] } : (p || {});
      var name = 'P' + (i + 1);
      return {
        id: i + 1, name: name,
        arrival: needInt(o.arrival === undefined ? 0 : o.arrival, 0, name + ' arrival time'),
        burst: needInt(o.burst, 1, name + ' burst time'),
        priority: needPriority ? needInt(o.priority, null, name + ' priority')
          : (blank(o.priority) || !isFinite(toNum(o.priority)) ? null : toNum(o.priority))
      };
    });
    var span = P.reduce(function (m, p) { return Math.max(m, p.arrival); }, 0) +
      P.reduce(function (s, p) { return s + p.burst; }, 0);
    if (span > MAX_TIME) throw new Error('Too much work to simulate (more than ' + MAX_TIME + ' time units)');
    return P;
  }

  /** [{C, D, T}] or [[C, D, T]] -> normalised task list (D defaults to T). */
  function normTasks(list) {
    if (!Array.isArray(list) || list.length === 0) throw new Error('Add at least one task');
    return list.map(function (p, i) {
      var o = Array.isArray(p) ? { C: p[0], D: p[1], T: p[2] } : (p || {});
      var name = 'P' + (i + 1);
      var C = needInt(o.C, 1, name + ' processing time C');
      var T = needInt(o.T, 1, name + ' period T');
      var D = needInt(blank(o.D) ? T : o.D, 1, name + ' deadline D');
      return { id: i + 1, name: name, C: C, D: D, T: T };
    });
  }

  /** "4,8,FCFS" or [4, 8, null] -> [4, 8, null]. Only the last level may be FCFS. */
  function parseQuanta(q) {
    var arr = q;
    if (typeof q === 'number') arr = [q];
    if (typeof q === 'string') arr = q.split(/[\s,;]+/).filter(Boolean);
    if (!Array.isArray(arr) || arr.length === 0) throw new Error('MLFQ needs at least one queue, e.g. "4,8,FCFS"');
    return arr.map(function (x, i) {
      if (x === null || /^(fcfs|inf|infinity|none|null|-)$/i.test(String(x).trim())) {
        if (i !== arr.length - 1) throw new Error('Only the last MLFQ queue can be FCFS');
        return null;
      }
      return needInt(x, 1, 'Quantum of Q' + i);
    });
  }

  /** Explain why `chosen` beat the processes that tie with it on the primary key. */
  function tieNote(chosen, cands, prim, run, mode) {
    var pc = prim(chosen);
    var rivals = cands.filter(function (p) { return p !== chosen && prim(p) === pc; });
    if (!rivals.length) return '';
    var head = '; tie with ' + names(rivals) + ' -> ';
    if (chosen === run) return head + 'the running process keeps the CPU';
    if (mode === 'preempt' && run && rivals.indexOf(run) >= 0) return head + 'the newly arrived process wins';
    if (rivals.every(function (p) { return p.arrival > chosen.arrival; })) return head + 'earlier arrival';
    if (rivals.every(function (p) { return p.arrival === chosen.arrival; })) return head + 'lower id';
    return head + 'earlier arrival, then lower id';
  }

  /* ======================================================== RR and FCFS */
  /* q = null -> FCFS. A process whose quantum expires at t joins the tail AFTER
     the processes arriving at t (course rule) unless arrivalFirst === false. */
  function simRR(P, q, arrivalFirst) {
    var rem = remMap(P), firstEnd = {}, blocks = [], log = [];
    var pending = P.slice().sort(byArrival), queue = [];
    var t = 0, run = null, used = 0, carry = [], idleLogged = false;
    var lab = function (p) { return p.name + '(' + rem[p.name] + ')'; };
    while (pending.length || queue.length || run) {
      var ev = carry; carry = [];
      var expired = null;
      if (run && q !== null && used === q) {
        expired = run; run = null;
        setOnce(firstEnd, expired.name, t);
      }
      var requeue = function () {
        queue.push(expired);
        ev.push(expired.name + ' used its full quantum (' + q + '), ' + rem[expired.name] +
          ' left -> tail of ready queue');
      };
      if (expired && !arrivalFirst) requeue();
      while (pending.length && pending[0].arrival <= t) {
        var p = pending.shift();
        queue.push(p);
        ev.push(p.name + ' arrives (burst ' + p.burst + ') -> tail of ready queue');
      }
      if (expired && arrivalFirst) requeue();

      var why = '', switched = false;
      if (!run) {
        if (!queue.length) {
          if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'nothing is ready', fmtQ(queue, lab)));
          idleLogged = true;
          blocks.push(blk(t, t + 1, 'idle')); t++;
          continue;
        }
        run = queue.shift(); used = 0; switched = true;
        if (run === expired) why = 'nobody else is waiting, so it continues with a new quantum';
        else why = q === null ? 'head of the ready queue (FCFS, runs to completion)'
          : 'head of the ready queue, gets a quantum of ' + q;
      } else if (ev.length) {
        why = q === null ? 'keeps the CPU (FCFS is non-preemptive)'
          : 'keeps the CPU (' + used + ' of its quantum ' + q + ' used)';
      }
      if (switched || ev.length) log.push(entry(t, ev, run.name, why, fmtQ(queue, lab)));
      idleLogged = false;
      blocks.push(blk(t, t + 1, run.name));
      rem[run.name]--; used++; t++;
      if (rem[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        carry.push(run.name + ' finishes');
        run = null;
      }
    }
    if (carry.length) log.push(entry(t, carry, '-', 'all processes have finished', ''));
    return { blocks: merge(blocks), firstEnd: firstEnd, log: log };
  }

  /* ============================================ SJF / SRTF / Priority */
  /* Shared engine: pick the ready process with the smallest key
     [primary, runningBit, arrival, id]. Non-preemptive: decide only when the
     CPU is free. tie 'keep' -> on a primary tie the running process wins;
     'preempt' -> the running process loses ties (a newly arrived one wins). */
  function simSelect(P, cfg) {
    var rem = remMap(P), firstEnd = {}, blocks = [], log = [];
    var t = 0, run = null, carry = [], idleLogged = false;
    var prim = function (p) { return cfg.prim(p, rem); };
    var runBit = function (p) {
      if (cfg.tie === 'preempt') return p === run ? 1 : 0;
      return p === run ? 0 : 1;
    };
    var waitKey = function (p) { return [prim(p), p.arrival, p.id]; };
    while (anyLeft(P, rem)) {
      var ev = carry; carry = [];
      P.forEach(function (p) {
        if (p.arrival === t) ev.push(p.name + ' arrives (' + cfg.arrivalInfo(p) + ')');
      });
      var ready = P.filter(function (p) { return p.arrival <= t && rem[p.name] > 0; });
      if (!ready.length) {
        if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'nothing is ready', '[ ]'));
        idleLogged = true;
        blocks.push(blk(t, t + 1, 'idle')); t++;
        continue;
      }
      var why = '', switched = false;
      if (!run || cfg.preemptive) {
        var nw = argmin(ready, function (p) { return [prim(p), runBit(p), p.arrival, p.id]; });
        var tn = tieNote(nw, ready, prim, run, cfg.tie);
        if (run && nw !== run) {
          setOnce(firstEnd, run.name, t);
          ev.push(nw.name + ' (' + cfg.show(nw, rem) + ') preempts ' + run.name + ' (' + cfg.show(run, rem) + ')');
          why = cfg.best(nw, rem) + tn;
        } else if (!run) {
          why = cfg.best(nw, rem) + tn;
        } else if (ev.length) {
          why = 'keeps the CPU: ' + cfg.best(nw, rem) + tn;
        }
        switched = nw !== run;
        run = nw;
      } else if (ev.length) {
        why = 'keeps the CPU (non-preemptive)';
      }
      if (switched || ev.length) {
        var waiting = ready.filter(function (p) { return p !== run; });
        waiting.sort(function (a, b) { return lexLess(waitKey(a), waitKey(b)) ? -1 : 1; });
        log.push(entry(t, ev, run.name, why, fmtQ(waiting, function (p) { return cfg.qlab(p, rem); })));
      }
      idleLogged = false;
      blocks.push(blk(t, t + 1, run.name));
      rem[run.name]--; t++;
      if (rem[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        carry.push(run.name + ' finishes');
        run = null;
      }
    }
    if (carry.length) log.push(entry(t, carry, '-', 'all processes have finished', ''));
    return { blocks: merge(blocks), firstEnd: firstEnd, log: log };
  }

  function simSJF(P, preemptive, tie) {
    return simSelect(P, {
      preemptive: preemptive, tie: tie,
      prim: function (p, rem) { return rem[p.name]; },
      arrivalInfo: function (p) { return 'burst ' + p.burst; },
      show: function (p, rem) { return 'remaining ' + rem[p.name]; },
      best: function (p, rem) {
        return preemptive ? 'shortest remaining time (' + rem[p.name] + ')'
          : 'shortest next CPU burst (' + rem[p.name] + ')';
      },
      qlab: function (p, rem) { return p.name + '(' + rem[p.name] + ')'; }
    });
  }

  function simPriority(P, preemptive, smallerIsHigher) {
    var sign = smallerIsHigher ? 1 : -1;
    var order = smallerIsHigher ? 'smaller number = higher' : 'larger number = higher';
    return simSelect(P, {
      preemptive: preemptive, tie: 'keep',
      prim: function (p) { return sign * p.priority; },
      arrivalInfo: function (p) { return 'burst ' + p.burst + ', priority ' + p.priority; },
      show: function (p) { return 'priority ' + p.priority; },
      best: function (p) { return 'highest priority (' + p.priority + '; ' + order + ')'; },
      qlab: function (p, rem) { return p.name + '(pri ' + p.priority + ', ' + rem[p.name] + ' left)'; }
    });
  }

  /* ======================================================= Priority + RR */
  /* One FIFO queue per priority value; the highest non-empty level runs, RR with
     quantum q inside a level. A higher-priority arrival preempts; the preempted
     process goes back to the HEAD of its level and keeps the rest of its quantum
     (same rule as the course MLFQ). */
  function simPriorityRR(P, q, smallerIsHigher, arrivalFirst) {
    var rem = remMap(P), firstEnd = {}, blocks = [], log = [], usedQ = {};
    var queues = {};
    P.forEach(function (p) { queues[p.priority] = queues[p.priority] || []; });
    var prios = Object.keys(queues).map(Number).sort(function (a, b) {
      return smallerIsHigher ? a - b : b - a;
    });
    var higher = function (a, b) { return smallerIsHigher ? a < b : a > b; };
    var bestLevel = function () {
      for (var i = 0; i < prios.length; i++) if (queues[prios[i]].length) return prios[i];
      return null;
    };
    var lab = function (p) {
      var u = usedQ[p.name] || 0;
      return p.name + '(' + rem[p.name] + (u ? '; ' + (q - u) + ' of quantum left' : '') + ')';
    };
    var snapshot = function () {
      var busy = prios.filter(function (pr) { return queues[pr].length; });
      return busy.length ? busy.map(function (pr) { return 'pri ' + pr + ' ' + fmtQ(queues[pr], lab); }).join('  ') : '[ ]';
    };
    var pending = P.slice().sort(byArrival);
    var t = 0, run = null, used = 0, carry = [], idleLogged = false;
    while (pending.length || run || bestLevel() !== null) {
      var ev = carry; carry = [];
      var expired = null;
      if (run && used === q) {
        expired = run; run = null; usedQ[expired.name] = 0;
        setOnce(firstEnd, expired.name, t);
      }
      var requeue = function () {
        queues[expired.priority].push(expired);
        ev.push(expired.name + ' used its full quantum (' + q + '), ' + rem[expired.name] +
          ' left -> tail of the priority-' + expired.priority + ' queue');
      };
      if (expired && !arrivalFirst) requeue();
      while (pending.length && pending[0].arrival <= t) {
        var p = pending.shift();
        queues[p.priority].push(p);
        ev.push(p.name + ' arrives (burst ' + p.burst + ', priority ' + p.priority +
          ') -> tail of the priority-' + p.priority + ' queue');
      }
      if (expired && arrivalFirst) requeue();
      if (run) {
        var b0 = bestLevel();
        if (b0 !== null && higher(b0, run.priority)) {
          usedQ[run.name] = used;
          setOnce(firstEnd, run.name, t);
          queues[run.priority].unshift(run);
          ev.push(run.name + ' (priority ' + run.priority + ') is preempted by ' + queues[b0][0].name +
            ' (priority ' + b0 + ') -> head of the priority-' + run.priority + ' queue, keeps ' +
            (q - used) + ' of its quantum');
          run = null;
        }
      }
      var why = '', switched = false;
      if (!run) {
        var b = bestLevel();
        if (b === null) {
          if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'nothing is ready', snapshot()));
          idleLogged = true;
          blocks.push(blk(t, t + 1, 'idle')); t++;
          continue;
        }
        run = queues[b].shift(); used = usedQ[run.name] || 0; switched = true;
        if (run === expired) why = 'no other priority-' + b + ' process is waiting, so it continues with a new quantum';
        else why = 'highest priority level present (' + b + '), head of its queue' +
          (used ? ', resumes with ' + (q - used) + ' of its quantum left' : ', quantum ' + q);
      } else if (ev.length) {
        why = 'keeps the CPU (nothing of higher priority; ' + used + ' of quantum ' + q + ' used)';
      }
      if (switched || ev.length) log.push(entry(t, ev, run.name, why, snapshot()));
      idleLogged = false;
      blocks.push(blk(t, t + 1, run.name));
      rem[run.name]--; used++; t++;
      if (rem[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        carry.push(run.name + ' finishes');
        usedQ[run.name] = 0;
        run = null;
      }
    }
    if (carry.length) log.push(entry(t, carry, '-', 'all processes have finished', ''));
    return { blocks: merge(blocks), firstEnd: firstEnd, log: log };
  }

  /* ================================================================ MLFQ */
  /* quanta e.g. [4, 8, null]. New jobs enter the Q0 tail. Using the full quantum
     at level k -> tail of level k+1 (a finite last level stays put: RR there).
     Preempted by a job in a higher queue -> HEAD of its own queue, keeping the
     rest of its quantum. Optional aging (A > 0): a job waiting in any queue
     below Q0 has a timer that starts when it joins or returns to that queue;
     when it reaches A the job moves to the Q0 tail with a fresh Q0 quantum. */
  function simMLFQ(P, quanta, aging, arrivalFirst) {
    var L = quanta.length;
    var rem = remMap(P), firstEnd = {}, blocks = [], log = [];
    var level = {}, qleft = {}, since = {};
    var queues = quanta.map(function () { return []; });
    var pending = P.slice().sort(byArrival);
    var t = 0, run = null, carry = [], idleLogged = false, demoted = null;
    var qdesc = function (k) { return quanta[k] === null ? 'FCFS' : 'RR q=' + quanta[k]; };
    var lab = function (p) {
      var k = level[p.name], extra = [];
      if (quanta[k] !== null && qleft[p.name] < quanta[k]) extra.push(qleft[p.name] + ' of quantum left');
      if (aging && k > 0) extra.push('ages at ' + (since[p.name] + aging));
      return p.name + '(' + rem[p.name] + (extra.length ? '; ' + extra.join('; ') : '') + ')';
    };
    var snapshot = function () {
      return queues.map(function (qq, k) { return 'Q' + k + ' ' + fmtQ(qq, lab); }).join('  ');
    };
    var someQueued = function () { return queues.some(function (qq) { return qq.length; }); };
    while (pending.length || run || demoted || someQueued()) {
      var ev = carry; carry = [];
      var pushDemoted = function () {
        if (!demoted) return;
        queues[level[demoted.name]].push(demoted);
        since[demoted.name] = t;
        demoted = null;
      };
      if (!arrivalFirst) pushDemoted();
      while (pending.length && pending[0].arrival <= t) {
        var p = pending.shift();
        level[p.name] = 0; qleft[p.name] = quanta[0];
        queues[0].push(p);
        ev.push(p.name + ' arrives (burst ' + p.burst + ') -> tail of Q0');
      }
      if (arrivalFirst) pushDemoted();
      if (aging) {
        for (var k = 1; k < L; k++) {
          var stay = [];
          for (var i = 0; i < queues[k].length; i++) {
            var w = queues[k][i];
            if (t - since[w.name] >= aging) {
              level[w.name] = 0; qleft[w.name] = quanta[0];
              queues[0].push(w);
              ev.push(w.name + ' has waited ' + aging + ' in Q' + k + ' -> moves to the tail of Q0 (aging)');
            } else stay.push(w);
          }
          queues[k] = stay;
        }
      }
      if (run) {
        var lv = level[run.name], hk = -1;
        for (var j = 0; j < lv; j++) if (queues[j].length) { hk = j; break; }
        if (hk >= 0) {
          queues[lv].unshift(run);
          since[run.name] = t;
          setOnce(firstEnd, run.name, t);
          ev.push(run.name + ' (Q' + lv + ') is preempted by ' + queues[hk][0].name + ' in Q' + hk +
            ' -> head of Q' + lv + (quanta[lv] !== null ? ', keeps ' + qleft[run.name] + ' of its quantum' : '') +
            (aging ? ', aging timer reset' : ''));
          run = null;
        }
      }
      var why = '', switched = false;
      if (!run) {
        var lvl = -1;
        for (var m = 0; m < L; m++) if (queues[m].length) { lvl = m; break; }
        if (lvl < 0) {
          if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'all queues are empty', snapshot()));
          idleLogged = true;
          blocks.push(blk(t, t + 1, 'idle')); t++;
          continue;
        }
        run = queues[lvl].shift(); switched = true;
        why = (lvl > 0 ? (lvl === 1 ? 'Q0 is empty' : 'Q0-Q' + (lvl - 1) + ' are empty') + ' -> ' : '') +
          'head of Q' + lvl + ' (' + qdesc(lvl) + ')';
        if (quanta[lvl] !== null) {
          why += qleft[run.name] < quanta[lvl] ? ', resumes with ' + qleft[run.name] + ' of its quantum left'
            : ', gets a quantum of ' + quanta[lvl];
        }
      } else if (ev.length) {
        var cl = level[run.name];
        why = 'keeps the CPU (no job in a higher queue' +
          (quanta[cl] !== null ? '; ' + qleft[run.name] + ' of its quantum left' : '') + ')';
      }
      if (switched || ev.length) log.push(entry(t, ev, run.name + '@Q' + level[run.name], why, snapshot()));
      idleLogged = false;
      var cur = level[run.name];
      blocks.push(blk(t, t + 1, run.name, cur));
      rem[run.name]--;
      if (qleft[run.name] !== null) qleft[run.name]--;
      t++;
      if (rem[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        carry.push(run.name + ' finishes');
        run = null;
      } else if (qleft[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        var nl = Math.min(cur + 1, L - 1);
        level[run.name] = nl; qleft[run.name] = quanta[nl];
        carry.push(run.name + ' used its full Q' + cur + ' quantum (' + quanta[cur] + '), ' + rem[run.name] +
          ' left -> ' + (nl > cur ? 'demoted to the tail of Q' + nl : 'back to the tail of Q' + nl));
        demoted = run;
        run = null;
      }
    }
    if (carry.length) log.push(entry(t, carry, '-', 'all processes have finished', ''));
    return { blocks: merge(blocks), firstEnd: firstEnd, log: log };
  }

  /* ==================================================== dynamic priority */
  /* Larger value = higher priority. priority = init + alpha*waited + beta*ran.
     Decide at t=0 (first arrival), every `every` units of the current run and
     whenever the CPU becomes free. Ties -> larger id (default) or smaller id. */
  function simDynamic(P, alpha, beta, init, every, tieLarger) {
    var rem = remMap(P), waited = {}, ran = {}, firstEnd = {}, blocks = [], log = [];
    P.forEach(function (p) { waited[p.name] = 0; ran[p.name] = 0; });
    var t = 0, run = null, slice = 0, carry = [], idleLogged = false;
    var prio = function (p) { return round9(init + alpha * waited[p.name] + beta * ran[p.name]); };
    var term = function (c, x) { return (c < 0 ? ' - ' + fmt(-c, 4) : ' + ' + fmt(c, 4)) + '*' + x; };
    var formula = function (p) {
      return p.name + ' = ' + fmt(init, 4) + term(alpha, waited[p.name]) + term(beta, ran[p.name]) + ' = ' + fmt(prio(p), 4);
    };
    while (anyLeft(P, rem)) {
      var ev = carry; carry = [];
      P.forEach(function (p) {
        if (p.arrival === t) ev.push(p.name + ' arrives (burst ' + p.burst + ', priority ' + fmt(init, 4) + ')');
      });
      var ready = P.filter(function (p) { return p.arrival <= t && rem[p.name] > 0; });
      if (!ready.length) {
        if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'nothing is ready', ''));
        idleLogged = true;
        blocks.push(blk(t, t + 1, 'idle')); t++;
        continue;
      }
      var why = '', decided = false, queue = '';
      if (!run || slice === every) {
        decided = true;
        var trigger = !run ? 'CPU is free' : 'check after ' + units(every) + ' of running';
        var best = argmin(ready, function (p) { return [-prio(p), tieLarger ? -p.id : p.id]; });
        var bp = prio(best);
        var rivals = ready.filter(function (p) { return p !== best && prio(p) === bp; });
        why = trigger + ' -> highest priority ' + fmt(bp, 4) +
          (rivals.length ? '; tie with ' + names(rivals) + ' -> ' + (tieLarger ? 'larger' : 'smaller') + ' id' : '');
        if (run && best !== run) {
          setOnce(firstEnd, run.name, t);
          ev.push(best.name + ' takes the CPU from ' + run.name);
        } else if (run) {
          why += ' (' + run.name + ' continues)';
        }
        queue = ready.map(formula).join('  ');
        run = best; slice = 0;
      } else if (ev.length) {
        why = 'keeps the CPU until the next check (' + slice + ' of ' + every + ' units used)';
        queue = ready.map(formula).join('  ');
      }
      if (decided || ev.length) log.push(entry(t, ev, run.name, why, queue));
      idleLogged = false;
      ready.forEach(function (p) { if (p === run) ran[p.name]++; else waited[p.name]++; });
      blocks.push(blk(t, t + 1, run.name));
      rem[run.name]--; slice++; t++;
      if (rem[run.name] === 0) {
        setOnce(firstEnd, run.name, t);
        carry.push(run.name + ' finishes');
        run = null;
      }
    }
    if (carry.length) log.push(entry(t, carry, '-', 'all processes have finished', ''));
    return { blocks: merge(blocks), firstEnd: firstEnd, log: log };
  }

  /* ============================================================ RM / EDF */
  /* Periodic tasks (C, D relative deadline, T period), all released at 0,
     simulated over [0, horizon). Late jobs keep running (soft real-time).
     RM key = period, EDF key = absolute deadline. tie 'keepRunning': the job
     that ran in the previous unit wins a tie on the key, otherwise smaller task
     id, then earlier release; 'smallerId': smaller task id, then earlier release. */
  function simRT(tasks, horizon, policy, tie) {
    var jobs = [], blocks = [], log = [];
    var t = 0, last = null, carry = [], idleLogged = false;
    var prim = function (j) { return policy === 'RM' ? j.task.T : j.deadline; };
    var key = function (j) {
      return tie === 'keepRunning' ? [prim(j), j === last ? 0 : 1, j.task.id, j.release]
        : [prim(j), j.task.id, j.release];
    };
    var jn = function (j) { return j.task.name + '#' + j.k; };
    var lab = function (j) { return jn(j) + '(d=' + j.deadline + ', ' + j.rem + ' left)'; };
    var missesAt = function (time, ev) {
      jobs.forEach(function (j) {
        if (j.rem > 0 && j.deadline === time) {
          ev.push(jn(j) + ' MISSES its deadline ' + time + ' (' + units(j.rem) + ' left; keeps running)');
        }
      });
    };
    while (t < horizon) {
      var ev = carry; carry = [];
      tasks.forEach(function (tk) {
        if (t % tk.T === 0) {
          var nj = { task: tk, k: t / tk.T + 1, release: t, deadline: t + tk.D, rem: tk.C, finish: null };
          jobs.push(nj);
          ev.push(jn(nj) + ' released (C=' + tk.C + ', deadline ' + nj.deadline + ')');
        }
      });
      missesAt(t, ev);
      var ready = jobs.filter(function (j) { return j.rem > 0; });
      if (!ready.length) {
        if (!idleLogged || ev.length) log.push(entry(t, ev, 'idle', 'no job is ready', '[ ]'));
        idleLogged = true; last = null;
        blocks.push(blk(t, t + 1, 'idle')); t++;
        continue;
      }
      var j = argmin(ready, key);
      var switched = j !== last;
      if (switched || ev.length) {
        var pv = prim(j);
        var rivals = ready.filter(function (x) { return x !== j && prim(x) === pv; });
        var why = policy === 'RM' ? 'shortest period (T=' + j.task.T + ')' : 'earliest absolute deadline (' + j.deadline + ')';
        if (rivals.length) {
          var how = j === last ? 'the running job keeps the CPU'
            : rivals.every(function (x) { return x.task.id === j.task.id; }) ? 'earlier release' : 'smaller task id';
          why += '; tie with ' + rivals.map(jn).join(', ') + ' -> ' + how;
        }
        if (!switched) why = 'keeps the CPU: ' + why;
        if (last && switched && last.rem > 0) ev.push(jn(j) + ' preempts ' + jn(last));
        var waiting = ready.filter(function (x) { return x !== j; });
        waiting.sort(function (a, b) { return lexLess(key(a), key(b)) ? -1 : 1; });
        log.push(entry(t, ev, jn(j), why, fmtQ(waiting, lab)));
      }
      idleLogged = false;
      blocks.push(blk(t, t + 1, j.task.name));
      j.rem--; t++;
      if (j.rem === 0) {
        j.finish = t;
        carry.push(jn(j) + ' finishes (' + (t <= j.deadline ? 'deadline ' + j.deadline + ' met'
          : 'LATE, deadline was ' + j.deadline) + ')');
        last = null;
      } else last = j;
    }
    missesAt(horizon, carry);
    if (carry.length) log.push(entry(horizon, carry, '-', 'end of the simulated window', ''));
    var out = jobs.map(function (x) {
      var status = x.finish !== null && x.finish <= x.deadline ? 'met' : (x.deadline <= horizon ? 'missed' : 'open');
      return { task: x.task.name, k: x.k, C: x.task.C, release: x.release, deadline: x.deadline,
        finish: x.finish, remaining: x.rem, status: status };
    });
    return { blocks: merge(blocks), jobs: out, log: log };
  }

  /* ================================================================ stats */

  function average(vals) {
    if (!vals.length || vals.some(function (v) { return v === null || v === undefined; })) return null;
    var n = vals.length, sum = vals.reduce(function (a, b) { return a + b; }, 0), value = sum / n;
    var list = vals.map(function (v) { return v < 0 ? '(' + fmt(v) + ')' : fmt(v); }).join('+');
    var text = n > 1 ? '(' + list + ')/' + n + ' = ' + fmt(sum) + '/' + n + ' = ' + fmt(value)
      : list + '/1 = ' + fmt(value);
    return { values: vals, sum: sum, n: n, value: value, text: text };
  }

  /** procs: normalised list (or raw [[arrival, burst]]); blocks: merged runs;
      firstRunEnd: {name: time the first run ended} or null. */
  function stats(procs, blocks, firstRunEnd) {
    var P = procs.length && procs[0].name ? procs : normProcs(procs, false);
    var comp = {}, first = {};
    blocks.forEach(function (b) {
      if (b.name === 'idle') return;
      comp[b.name] = b.end;
      setOnce(first, b.name, b.start);
    });
    var rows = P.map(function (p) {
      var c = comp[p.name], tat = c - p.arrival;
      var fe = firstRunEnd && firstRunEnd[p.name] !== undefined ? firstRunEnd[p.name] : null;
      return {
        name: p.name, id: p.id, arrival: p.arrival, burst: p.burst, priority: p.priority,
        completion: c, tat: tat, wt: tat - p.burst,
        firstStart: first[p.name], firstRunEnd: fe,
        rtStart: first[p.name] - p.arrival, rtCourse: fe === null ? null : fe - p.arrival
      };
    });
    var col = function (k) { return rows.map(function (r) { return r[k]; }); };
    return { rows: rows, avg: { tat: average(col('tat')), wt: average(col('wt')),
      rtCourse: average(col('rtCourse')), rtStart: average(col('rtStart')) } };
  }

  function gcd(a, b) { while (b) { var r = a % b; a = b; b = r; } return a; }

  /* ============================================================ metadata */

  var ALGOS = [
    { id: 'fcfs', name: 'FCFS', fields: ['arrival', 'burst'], params: [] },
    { id: 'sjf', name: 'SJF (non-preemptive)', fields: ['arrival', 'burst'], params: [] },
    { id: 'srtf', name: 'SRTF (preemptive SJF)', fields: ['arrival', 'burst'], params: ['srtfTie'] },
    { id: 'rr', name: 'Round Robin', fields: ['arrival', 'burst'], params: ['q', 'arrivalFirst'] },
    { id: 'priority', name: 'Priority', fields: ['arrival', 'burst', 'priority'], params: ['preemptive', 'smallerIsHigher'] },
    { id: 'priority-rr', name: 'Priority + RR', fields: ['arrival', 'burst', 'priority'], params: ['q', 'smallerIsHigher', 'arrivalFirst'] },
    { id: 'mlfq', name: 'MLFQ', fields: ['arrival', 'burst'], params: ['quanta', 'aging'] },
    { id: 'dynamic', name: 'Dynamic priority', fields: ['arrival', 'burst'], params: ['alpha', 'beta', 'init', 'checkEvery', 'dynTie'] },
    { id: 'rm', name: 'Rate Monotonic (RM)', rt: true, fields: ['C', 'D', 'T'], params: ['horizon', 'rtTie'] },
    { id: 'edf', name: 'Earliest Deadline First (EDF)', rt: true, fields: ['C', 'D', 'T'], params: ['horizon', 'rtTie'] }
  ];
  var ALGO_BY_ID = {};
  ALGOS.forEach(function (a) { ALGO_BY_ID[a.id] = a; });

  var DEFAULTS = {
    q: 4, arrivalFirst: true, srtfTie: 'keep', preemptive: false, smallerIsHigher: true,
    quanta: '4,8,FCFS', aging: 0, alpha: 0, beta: 3, init: 0, checkEvery: 1, dynTie: 'larger',
    horizon: 16, rtTie: 'keepRunning'
  };

  /* ================================================================== run */
  /**
   * run(algo, procs, opts) -> result
   *  algo : 'fcfs'|'sjf'|'srtf'|'rr'|'priority'|'priority-rr'|'mlfq'|'dynamic'|'rm'|'edf'
   *  procs: [{arrival, burst, priority?}] or [[arrival, burst, priority?]];
   *         for rm/edf: [{C, D, T}] or [[C, D, T]]
   *  opts : see DEFAULTS. Throws Error with a readable message on bad input.
   */
  function run(algo, procs, opts) {
    var meta = ALGO_BY_ID[algo];
    if (!meta) throw new Error('Unknown algorithm "' + algo + '"');
    var o = {};
    Object.keys(DEFAULTS).forEach(function (k) { o[k] = DEFAULTS[k]; });
    Object.keys(opts || {}).forEach(function (k) { if (opts[k] !== undefined) o[k] = opts[k]; });
    var arrivalFirst = o.arrivalFirst !== false;
    var smaller = o.smallerIsHigher !== false;

    if (meta.rt) {
      var T = normTasks(procs);
      var horizon = needInt(o.horizon, 1, 'Horizon');
      if (horizon > MAX_TIME) throw new Error('Horizon must be at most ' + MAX_TIME);
      var tie = o.rtTie === 'smallerId' ? 'smallerId' : 'keepRunning';
      var rt = simRT(T, horizon, algo === 'rm' ? 'RM' : 'EDF', tie);
      var U = T.reduce(function (s, x) { return s + x.C / x.T; }, 0);
      var n = T.length, bound = n * (Math.pow(2, 1 / n) - 1);
      var hyper = T.reduce(function (l, x) { return l === null || l > 1e9 ? null : l / gcd(l, x.T) * x.T; }, 1);
      return {
        algo: algo, name: meta.name, kind: 'rt', opts: o, tasks: T, horizon: horizon,
        blocks: rt.blocks, gantt: ganttString(rt.blocks), log: rt.log, jobs: rt.jobs,
        misses: rt.jobs.filter(function (j) { return j.status === 'missed'; }),
        util: { value: U, text: T.map(function (x) { return x.C + '/' + x.T; }).join(' + ') + ' = ' + fmt(U, 3) },
        rmBound: { n: n, value: bound, text: n + '(2^(1/' + n + ') - 1) = ' + fmt(bound, 3) },
        hyperperiod: hyper !== null && hyper <= 1e9 ? hyper : null
      };
    }

    var P = normProcs(procs, meta.fields.indexOf('priority') >= 0);
    var r;
    switch (algo) {
      case 'fcfs': r = simRR(P, null, true); break;
      case 'rr': r = simRR(P, needInt(o.q, 1, 'Quantum q'), arrivalFirst); break;
      case 'sjf': r = simSJF(P, false, 'keep'); break;
      case 'srtf': r = simSJF(P, true, o.srtfTie === 'preempt' ? 'preempt' : 'keep'); break;
      case 'priority': r = simPriority(P, !!o.preemptive, smaller); break;
      case 'priority-rr': r = simPriorityRR(P, needInt(o.q, 1, 'Quantum q'), smaller, arrivalFirst); break;
      case 'mlfq': {
        var aging = blank(o.aging) || o.aging === false ? 0 : needInt(o.aging, 0, 'Aging threshold');
        r = simMLFQ(P, parseQuanta(o.quanta), aging, arrivalFirst);
        break;
      }
      case 'dynamic':
        r = simDynamic(P, needNum(o.alpha, 'alpha'), needNum(o.beta, 'beta'), needNum(o.init, 'Initial priority'),
          needInt(o.checkEvery, 1, 'Check interval'), o.dynTie !== 'smaller');
        break;
    }
    var st = stats(P, r.blocks, r.firstEnd);
    return {
      algo: algo, name: meta.name, kind: 'proc', opts: o, procs: P,
      blocks: r.blocks, gantt: ganttString(r.blocks), log: r.log, rows: st.rows, avg: st.avg
    };
  }

  /* ============================================================= presets */
  /* Every worked example used by the test-suite (ids match test_sched.js). */
  var S26 = 'Spring 2026 midterm', F20 = 'Fall 2020 midterm', SP21 = 'Spring 2021 midterm',
    F19 = 'Fall 2019 midterm', LEC = 'Lecture slides (Ch. 5)', HW2 = 'HW2';
  var F19P = [[0, 8], [7, 13], [9, 1], [11, 5], [20, 7], [27, 1]];
  var F20P = [[0, 9], [3, 3], [8, 2], [10, 6], [16, 8], [20, 5]];
  var SP21P = [[0, 2], [4, 12], [6, 6], [9, 4], [13, 5]];
  var HW2P = [[0, 7], [1, 3], [4, 5], [10, 2]];
  var S26DP = [[0, 7], [3, 5], [6, 6], [9, 4]];
  var PRESETS = [
    { id: 's26-q41', group: S26, name: 'S26 Q4.1 MLFQ (4, 8, FCFS)', algo: 'mlfq',
      procs: [[0, 9], [2, 25], [6, 7], [14, 18], [45, 15], [58, 6]], opts: { quanta: '4,8,FCFS' } },
    { id: 's26-q42-rm', group: S26, name: 'S26 Q4.2 RM (0-16)', algo: 'rm',
      procs: [[1, 3, 4], [2, 4, 5], [2, 6, 7], [1, 5, 8]], opts: { horizon: 16 } },
    { id: 's26-q42-edf', group: S26, name: 'S26 Q4.2 EDF (0-16)', algo: 'edf',
      procs: [[1, 3, 4], [2, 4, 5], [2, 6, 7], [1, 5, 8]], opts: { horizon: 16 } },
    { id: 's26-q43a', group: S26, name: 'S26 Q4.3(a) Dynamic priority, a=0 b=3', algo: 'dynamic',
      procs: S26DP, opts: { alpha: 0, beta: 3, init: 0, checkEvery: 1, dynTie: 'larger' } },
    { id: 's26-q43b', group: S26, name: 'S26 Q4.3(b) Dynamic priority, a=1 b=0, every 3', algo: 'dynamic',
      procs: S26DP.slice(0, 2), opts: { alpha: 1, beta: 0, init: 0, checkEvery: 3, dynTie: 'larger' } },
    { id: 's26-q43c', group: S26, name: 'S26 Q4.3(c) Dynamic priority, a=1 b=-2 init 30, every 3', algo: 'dynamic',
      procs: S26DP, opts: { alpha: 1, beta: -2, init: 30, checkEvery: 3, dynTie: 'larger' } },

    { id: 'f20-q41-fcfs', group: F20, name: 'F20 Q4.1 FCFS', algo: 'fcfs', procs: F20P, opts: {} },
    { id: 'f20-q41-sjf', group: F20, name: 'F20 Q4.1 SJF', algo: 'sjf', procs: F20P, opts: {} },
    { id: 'f20-q41-srtf', group: F20, name: 'F20 Q4.1 SRTF', algo: 'srtf', procs: F20P, opts: {} },
    { id: 'f20-q42', group: F20, name: 'F20 Q4.2 MLFQ (RR 4, FCFS) with aging 8', algo: 'mlfq',
      procs: [[0, 9], [3, 3], [8, 2], [10, 9], [13, 4], [18, 5]], opts: { quanta: '4,FCFS', aging: 8 } },
    { id: 'f20-q43', group: F20, name: 'F20 Q4.3 Priority + RR q=4', algo: 'priority-rr',
      procs: [[0, 9, 2], [3, 3, 1], [8, 5, 4], [10, 2, 4], [16, 8, 5], [20, 5, 3]], opts: { q: 4, smallerIsHigher: true } },

    { id: 'sp21-q21-fcfs', group: SP21, name: 'Sp21 Q2.1 FCFS', algo: 'fcfs', procs: SP21P, opts: {} },
    { id: 'sp21-q21-sjf', group: SP21, name: 'Sp21 Q2.1 SJF', algo: 'sjf', procs: SP21P, opts: {} },
    { id: 'sp21-q21-rr8', group: SP21, name: 'Sp21 Q2.1 RR q=8', algo: 'rr', procs: SP21P, opts: { q: 8 } },
    { id: 'sp21-q21-srtf', group: SP21, name: 'Sp21 Q2.1 SRTF', algo: 'srtf', procs: SP21P, opts: {} },
    { id: 'sp21-q22', group: SP21, name: 'Sp21 Q2.2 MLFQ (2, 4, FCFS)', algo: 'mlfq',
      procs: [[0, 10], [10, 8], [8, 30], [16, 2], [22, 8], [6, 22]], opts: { quanta: '2,4,FCFS' } },
    { id: 'sp21-q23-edf', group: SP21, name: 'Sp21 Q2.3 EDF (0-14)', algo: 'edf',
      procs: [[1, 3, 3], [2, 4, 4]], opts: { horizon: 14, rtTie: 'keepRunning' } },
    { id: 'sp21-q23-rm', group: SP21, name: 'Sp21 Q2.3 RM (0-14)', algo: 'rm',
      procs: [[1, 3, 3], [2, 4, 4]], opts: { horizon: 14, rtTie: 'keepRunning' } },

    { id: 'f19-q34', group: F19, name: 'F19 Q3.4 EDF (0-38)', algo: 'edf',
      procs: [[4, 10, 10], [2, 16, 16], [8, 20, 20]], opts: { horizon: 38, rtTie: 'keepRunning' } },
    { id: 'f19-q36-fcfs', group: F19, name: 'F19 Q3.6 FCFS', algo: 'fcfs', procs: F19P, opts: {} },
    { id: 'f19-q36-sjf', group: F19, name: 'F19 Q3.6 SJF', algo: 'sjf', procs: F19P, opts: {} },
    { id: 'f19-q36-rr4', group: F19, name: 'F19 Q3.6 RR q=4', algo: 'rr', procs: F19P, opts: { q: 4 } },
    { id: 'f19-q36-srtf-keep', group: F19, name: 'F19 Q3.6 SRTF (tie: running process keeps CPU)', algo: 'srtf',
      procs: F19P, opts: { srtfTie: 'keep' } },
    { id: 'f19-q36-srtf-preempt', group: F19, name: 'F19 Q3.6 SRTF (tie: new arrival wins)', algo: 'srtf',
      procs: F19P, opts: { srtfTie: 'preempt' } },

    { id: 'lec-513', group: LEC, name: 'Lecture 5.13 RR q=4', algo: 'rr',
      procs: [[0, 24], [0, 3], [0, 3]], opts: { q: 4 } },
    { id: 'lec-523', group: LEC, name: 'Lecture 5.23 SRTF', algo: 'srtf',
      procs: [[0, 8], [1, 4], [2, 9], [3, 5]], opts: {} },
    { id: 'lec-526', group: LEC, name: 'Lecture 5.26 Priority (non-preemptive)', algo: 'priority',
      procs: [[0, 10, 3], [0, 1, 1], [0, 2, 4], [0, 1, 5], [0, 5, 2]], opts: { preemptive: false, smallerIsHigher: true } },
    { id: 'lec-527', group: LEC, name: 'Lecture 5.27 Priority + RR q=2', algo: 'priority-rr',
      procs: [[0, 4, 3], [0, 5, 2], [0, 8, 2], [0, 7, 1], [0, 3, 3]], opts: { q: 2, smallerIsHigher: true } },
    { id: 'lec-532', group: LEC, name: 'Lecture 5.32 MLFQ (4, 8, FCFS)', algo: 'mlfq',
      procs: [[0, 10], [2, 15], [5, 2], [12, 14], [18, 6]], opts: { quanta: '4,8,FCFS' } },
    { id: 'lec-550', group: LEC, name: 'Lecture 5.50 RM (missed deadline)', algo: 'rm',
      procs: [[25, 50, 50], [35, 80, 80]], opts: { horizon: 85 } },
    { id: 'lec-551', group: LEC, name: 'Lecture 5.51 EDF', algo: 'edf',
      procs: [[25, 50, 50], [35, 80, 80]], opts: { horizon: 160 } },

    { id: 'hw2-mlfq', group: HW2, name: 'HW2 MLFQ (4, 8, FCFS)', algo: 'mlfq',
      procs: [[0, 20], [1, 5], [11, 2]], opts: { quanta: '4,8,FCFS' } },
    { id: 'hw2-srtf', group: HW2, name: 'HW2 SRTF', algo: 'srtf', procs: HW2P, opts: {} },
    { id: 'hw2-rr3', group: HW2, name: 'HW2 RR q=3', algo: 'rr', procs: HW2P, opts: { q: 3 } }
  ];

  var Sched = {
    run: run,
    merge: merge,
    ganttString: ganttString,
    stats: stats,
    parseQuanta: parseQuanta,
    fmt: fmt,
    ALGOS: ALGOS,
    DEFAULTS: DEFAULTS,
    PRESETS: PRESETS
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = Sched;
  if (typeof window !== 'undefined') window.Sched = Sched;
})();
