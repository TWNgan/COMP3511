/* test_sched.js - asserts Midterm_Site/assets/sched.js against official answers.
 * Run: node C:\Code\UST\COMP3511\_work\midterm\scripts\test_sched.js
 */
'use strict';
const path = require('path');
const Sched = require(path.resolve(__dirname, '..', '..', '..', 'Midterm_Site', 'assets', 'sched.js'));

let pass = 0, fail = 0;
const failures = [];
function check(label, ok, detail) {
  if (ok) pass++;
  else { fail++; failures.push(label + (detail ? '\n      ' + detail : '')); }
}
function eq(label, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  check(label, g === w, 'got  ' + g + '\n      want ' + w);
}
function approx(label, got, want) {
  check(label, typeof got === 'number' && Math.abs(got - want) < 0.006, 'got ' + got + ', want ' + want);
}
const stripQ = (s) => s.replace(/@Q\d+/g, '');

/* ----------------------------------------------------------------- data */
const S26_MLFQ = [[0, 9], [2, 25], [6, 7], [14, 18], [45, 15], [58, 6]];
const F19 = [[0, 8], [7, 13], [9, 1], [11, 5], [20, 7], [27, 1]];
const F20 = [[0, 9], [3, 3], [8, 2], [10, 6], [16, 8], [20, 5]];
const SP21 = [[0, 2], [4, 12], [6, 6], [9, 4], [13, 5]];
const HW2 = [[0, 7], [1, 3], [4, 5], [10, 2]];
const S26_DYN = [[0, 7], [3, 5], [6, 6], [9, 4]];
const S26_RT = [[1, 3, 4], [2, 4, 5], [2, 6, 7], [1, 5, 8]];
const LEC_RT = [[25, 50, 50], [35, 80, 80]];

/* Each case id matches a Sched.PRESETS id (checked at the end). */
const CASES = [
  // ---- MLFQ
  { id: 's26-q41', algo: 'mlfq', procs: S26_MLFQ, opts: { quanta: [4, 8, null] },
    gantt: '0 P1@Q0 4 P2@Q0 8 P3@Q0 12 P1@Q1 14 P4@Q0 18 P1@Q1 21 P2@Q1 29 P3@Q1 32 P4@Q1 40 P2@Q2 45 P5@Q0 49 P5@Q1 57 P2@Q2 58 P6@Q0 62 P6@Q1 64 P2@Q2 71 P4@Q2 77 P5@Q2 80',
    wt: [12, 44, 19, 45, 20, 0], avgWT: 23.33, wtText: '(12+44+19+45+20+0)/6 = 140/6 = 23.33',
    rtCourse: [4, 6, 6, 4, 4, 4], avgRtCourse: 4.67, rtText: '(4+6+6+4+4+4)/6 = 28/6 = 4.67' },
  { id: 'lec-532', algo: 'mlfq', procs: [[0, 10], [2, 15], [5, 2], [12, 14], [18, 6]], opts: { quanta: '4,8,FCFS' },
    gantt: '0 P1@Q0 4 P2@Q0 8 P3@Q0 10 P1@Q1 12 P4@Q0 16 P1@Q1 18 P5@Q0 22 P1@Q1 24 P2@Q1 32 P4@Q1 40 P5@Q1 42 P2@Q2 45 P4@Q2 47',
    wt: [14, 28, 3, 21, 18], avgWT: 16.8 },
  { id: 'hw2-mlfq', algo: 'mlfq', procs: [[0, 20], [1, 5], [11, 2]], opts: { quanta: '4,8,FCFS' },
    gantt: '0 P1@Q0 4 P2@Q0 8 P1@Q1 11 P3@Q0 13 P1@Q1 18 P2@Q1 19 P1@Q2 27' },
  { id: 'sp21-q22', algo: 'mlfq', procs: [[0, 10], [10, 8], [8, 30], [16, 2], [22, 8], [6, 22]], opts: { quanta: '2,4,FCFS' },
    gantt: '0 P1@Q0 2 P1@Q1 6 P6@Q0 8 P3@Q0 10 P2@Q0 12 P6@Q1 16 P4@Q0 18 P3@Q1 22 P5@Q0 24 P2@Q1 28 P5@Q1 32 P1@Q2 36 P6@Q2 52 P3@Q2 76 P2@Q2 78 P5@Q2 80',
    wt: [26, 60, 38, 0, 50, 24], avgWT: 33 },
  { id: 'f20-q42', algo: 'mlfq', procs: [[0, 9], [3, 3], [8, 2], [10, 9], [13, 4], [18, 5]], opts: { quanta: '4,FCFS', aging: 8 },
    gantt: '0 P1 4 P2 7 P1 8 P3 10 P4 14 P5 18 P1 22 P6 26 P4 30 P6 31 P4 32', strip: true,
    wt: [13, 1, 0, 13, 1, 8], avgWT: 6 },

  // ---- RR / FCFS / SJF / SRTF
  { id: 'lec-513', algo: 'rr', procs: [[0, 24], [0, 3], [0, 3]], opts: { q: 4 },
    gantt: '0 P1 4 P2 7 P3 10 P1 30', wt: [6, 4, 7], rtCourse: [4, 7, 10], avgWT: 5.67, avgTAT: 15.67, avgRtCourse: 7 },
  { id: 'lec-523', algo: 'srtf', procs: [[0, 8], [1, 4], [2, 9], [3, 5]], opts: {},
    gantt: '0 P1 1 P2 5 P4 10 P1 17 P3 26', avgWT: 6.5 },
  { id: 'hw2-srtf', algo: 'srtf', procs: HW2, opts: {},
    gantt: '0 P1 1 P2 4 P3 9 P1 10 P4 12 P1 17', avgWT: 2.5, avgTAT: 6.75 },
  { id: 'hw2-rr3', algo: 'rr', procs: HW2, opts: { q: 3 },
    gantt: '0 P1 3 P2 6 P1 9 P3 12 P1 13 P4 15 P3 17', avgWT: 4.75, avgTAT: 9 },
  { id: 'f19-q36-fcfs', algo: 'fcfs', procs: F19, opts: {},
    gantt: '0 P1 8 P2 21 P3 22 P4 27 P5 34 P6 35', avgWT: 6.33 },
  { id: 'f19-q36-sjf', algo: 'sjf', procs: F19, opts: {},
    gantt: '0 P1 8 P2 21 P3 22 P4 27 P6 28 P5 35', avgWT: 5.33 },
  { id: 'f19-q36-rr4', algo: 'rr', procs: F19, opts: { q: 4 },
    gantt: '0 P1 8 P2 12 P3 13 P4 17 P2 21 P4 22 P5 26 P2 30 P5 33 P6 34 P2 35', avgWT: 6.0 },
  { id: 'f19-q36-srtf-keep', algo: 'srtf', procs: F19, opts: { srtfTie: 'keep' },
    gantt: '0 P1 8 P2 9 P3 10 P2 11 P4 16 P2 27 P6 28 P5 35', avgWT: 2.5 },
  { id: 'f19-q36-srtf-preempt', algo: 'srtf', procs: F19, opts: { srtfTie: 'preempt' },
    gantt: '0 P1 8 P2 9 P3 10 P2 11 P4 16 P2 20 P5 27 P6 28 P2 35', avgWT: 2.5 },
  { id: 'f20-q41-fcfs', algo: 'fcfs', procs: F20, opts: {},
    gantt: '0 P1 9 P2 12 P3 14 P4 20 P5 28 P6 33', avgWT: 4.33 },
  { id: 'f20-q41-sjf', algo: 'sjf', procs: F20, opts: {},
    gantt: '0 P1 9 P3 11 P2 14 P4 20 P6 25 P5 33', avgWT: 3.67 },
  { id: 'f20-q41-srtf', algo: 'srtf', procs: F20, opts: {},
    gantt: '0 P1 3 P2 6 P1 8 P3 10 P1 14 P4 20 P6 25 P5 33', avgWT: 3.0 },
  { id: 'sp21-q21-fcfs', algo: 'fcfs', procs: SP21, opts: {},
    gantt: '0 P1 2 idle 4 P2 16 P3 22 P4 26 P5 31', avgWT: 7.2 },
  { id: 'sp21-q21-sjf', algo: 'sjf', procs: SP21, opts: {}, avgWT: 6.6 },
  { id: 'sp21-q21-rr8', algo: 'rr', procs: SP21, opts: { q: 8 },
    gantt: '0 P1 2 idle 4 P2 12 P3 18 P4 22 P2 26 P5 31', avgWT: 7.6 },
  { id: 'sp21-q21-srtf', algo: 'srtf', procs: SP21, opts: {},
    gantt: '0 P1 2 idle 4 P2 6 P3 12 P4 16 P5 21 P2 31', avgWT: 4.2 },

  // ---- Priority
  { id: 'f20-q43', algo: 'priority-rr', procs: [[0, 9, 2], [3, 3, 1], [8, 5, 4], [10, 2, 4], [16, 8, 5], [20, 5, 3]],
    opts: { q: 4, smallerIsHigher: true },
    gantt: '0 P1 3 P2 6 P1 12 P3 16 P4 18 P3 19 P5 20 P6 25 P5 32', wt: [3, 0, 6, 6, 8, 0], avgWT: 3.83 },
  { id: 'lec-527', algo: 'priority-rr', procs: [[0, 4, 3], [0, 5, 2], [0, 8, 2], [0, 7, 1], [0, 3, 3]], opts: { q: 2 },
    gantt: '0 P4 7 P2 9 P3 11 P2 13 P3 15 P2 16 P3 20 P1 22 P5 24 P1 26 P5 27' },
  { id: 'lec-526', algo: 'priority', procs: [[0, 10, 3], [0, 1, 1], [0, 2, 4], [0, 1, 5], [0, 5, 2]], opts: { preemptive: false },
    gantt: '0 P2 1 P5 6 P1 16 P3 18 P4 19', avgWT: 8.2 },

  // ---- Dynamic priority (S26 Q4.3)
  { id: 's26-q43a', algo: 'dynamic', procs: S26_DYN, opts: { alpha: 0, beta: 3, init: 0, checkEvery: 1, dynTie: 'larger' },
    gantt: '0 P1 7 P3 13 P4 17 P2 22' },
  { id: 's26-q43b', algo: 'dynamic', procs: S26_DYN.slice(0, 2), opts: { alpha: 1, beta: 0, init: 0, checkEvery: 3 },
    gantt: '0 P1 3 P2 6 P1 9 P2 11 P1 12' },
  { id: 's26-q43c', algo: 'dynamic', procs: S26_DYN, opts: { alpha: 1, beta: -2, init: 30, checkEvery: 3 },
    gantt: '0 P1 3 P2 6 P3 9 P4 12 P1 15 P2 17 P3 20 P4 21 P1 22' },

  // ---- Real-time (misses: [task, deadline, finish|null])
  { id: 's26-q42-rm', algo: 'rm', procs: S26_RT, opts: { horizon: 16 }, bothTies: true,
    gantt: '0 P1 1 P2 3 P3 4 P1 5 P2 7 P3 8 P1 9 P3 10 P2 12 P1 13 P3 15 P2 16',
    misses: [['P3', 6, 8], ['P4', 5, null], ['P3', 13, 14], ['P4', 13, null]] },
  { id: 's26-q42-edf', algo: 'edf', procs: S26_RT, opts: { horizon: 16 }, bothTies: true,
    gantt: '0 P1 1 P2 3 P4 4 P3 6 P1 7 P2 9 P1 10 P3 12 P4 13 P2 15 P1 16',
    misses: [['P2', 14, 15], ['P1', 15, 16]] },
  { id: 'f19-q34', algo: 'edf', procs: [[4, 10, 10], [2, 16, 16], [8, 20, 20]], opts: { horizon: 38, rtTie: 'keepRunning' },
    gantt: '0 P1 4 P2 6 P3 14 P1 18 P2 20 P1 24 P3 32 P1 36 P2 38', misses: [], tieMatters: true },
  { id: 'sp21-q23-edf', algo: 'edf', procs: [[1, 3, 3], [2, 4, 4]], opts: { horizon: 14, rtTie: 'keepRunning' },
    gantt: '0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 10 P1 11 idle 12 P1 13 P2 14', misses: [], tieMatters: true },
  { id: 'sp21-q23-rm', algo: 'rm', procs: [[1, 3, 3], [2, 4, 4]], opts: { horizon: 14, rtTie: 'keepRunning' },
    gantt: '0 P1 1 P2 3 P1 4 P2 6 P1 7 idle 8 P2 9 P1 10 P2 11 idle 12 P1 13 P2 14', misses: [] },
  { id: 'lec-550', algo: 'rm', procs: LEC_RT, opts: { horizon: 85 },
    gantt: '0 P1 25 P2 50 P1 75 P2 85', misses: [['P2', 80, 85]] },
  { id: 'lec-551', algo: 'edf', procs: LEC_RT, opts: { horizon: 160 },
    gantt: '0 P1 25 P2 60 P1 85 P2 100 P1 125 P2 145 idle 150 P1 160', misses: [] }
];

/* ------------------------------------------------------------- checks */
function invariants(label, r) {
  // blocks are contiguous from 0, positive length, and every process gets exactly its burst
  let t = 0, okContig = true;
  const got = {};
  r.blocks.forEach((b) => {
    if (b.start !== t || b.end <= b.start) okContig = false;
    t = b.end;
    if (b.name !== 'idle') got[b.name] = (got[b.name] || 0) + (b.end - b.start);
  });
  check(label + ' blocks contiguous', okContig);
  if (r.kind === 'proc') {
    const okBurst = r.procs.every((p) => got[p.name] === p.burst);
    check(label + ' each process runs exactly its burst', okBurst, JSON.stringify(got));
    const okArr = r.procs.every((p) => r.blocks.every((b) => b.name !== p.name || b.start >= p.arrival));
    check(label + ' nobody runs before arrival', okArr);
    const okRt = r.rows.every((row) => row.rtCourse >= row.rtStart && row.rtCourse > 0 && row.wt >= 0);
    check(label + ' RT(course) >= RT(textbook), WT >= 0', okRt);
  } else {
    check(label + ' rt horizon', t === r.horizon, 'ends at ' + t);
  }
  check(label + ' log present', Array.isArray(r.log) && r.log.length > 0 &&
    r.log.every((e) => typeof e.t === 'number' && Array.isArray(e.events)));
}

function missList(r) {
  return r.misses.map((m) => [m.task, m.deadline, m.finish]).map((x) => JSON.stringify(x)).sort();
}

const results = {};
CASES.forEach((c) => {
  const label = c.id;
  let r;
  try { r = Sched.run(c.algo, c.procs, c.opts); } catch (e) { check(label + ' runs', false, e.stack); return; }
  results[c.id] = r;
  if (c.gantt) eq(label + ' gantt', c.strip ? stripQ(r.gantt) : r.gantt, c.gantt);
  if (c.wt) eq(label + ' WT', r.rows.map((x) => x.wt), c.wt);
  if (c.avgWT !== undefined) approx(label + ' avg WT', r.avg.wt.value, c.avgWT);
  if (c.avgTAT !== undefined) approx(label + ' avg TAT', r.avg.tat.value, c.avgTAT);
  if (c.rtCourse) eq(label + ' RT(course)', r.rows.map((x) => x.rtCourse), c.rtCourse);
  if (c.avgRtCourse !== undefined) approx(label + ' avg RT(course)', r.avg.rtCourse.value, c.avgRtCourse);
  if (c.wtText) eq(label + ' WT working', r.avg.wt.text, c.wtText);
  if (c.rtText) eq(label + ' RT working', r.avg.rtCourse.text, c.rtText);
  if (c.misses) {
    eq(label + ' misses', missList(r), c.misses.map((x) => JSON.stringify(x)).sort());
    eq(label + ' miss count', r.misses.length, c.misses.length);
  }
  if (c.bothTies) {
    ['keepRunning', 'smallerId'].forEach((tie) => {
      const r2 = Sched.run(c.algo, c.procs, Object.assign({}, c.opts, { rtTie: tie }));
      eq(label + ' gantt (rtTie=' + tie + ')', r2.gantt, c.gantt);
      eq(label + ' misses (rtTie=' + tie + ')', missList(r2), c.misses.map((x) => JSON.stringify(x)).sort());
    });
  }
  if (c.tieMatters) {
    const r2 = Sched.run(c.algo, c.procs, Object.assign({}, c.opts, { rtTie: 'smallerId' }));
    check(label + ' rtTie=smallerId gives a different chart', r2.gantt !== c.gantt, r2.gantt);
  }
  invariants(label, r);
});

// S26 Q4.2 utilisation and RM bound
{
  const r = results['s26-q42-rm'];
  approx('s26-q42 U', r.util.value, 1 / 4 + 2 / 5 + 2 / 7 + 1 / 8);
  approx('s26-q42 RM bound', r.rmBound.value, 4 * (Math.pow(2, 1 / 4) - 1));
  eq('s26-q42 hyperperiod', r.hyperperiod, 280);
}
// Course vs textbook RT columns (S26 MLFQ: textbook = first start - arrival)
eq('s26-q41 RT(textbook)', results['s26-q41'].rows.map((x) => x.rtStart), [0, 2, 2, 0, 0, 0]);
// SRTF tie option changes the course response time of P2 in F19 (no regression on WT)
approx('f19 srtf keep avg TAT', results['f19-q36-srtf-keep'].avg.tat.value, 8.33);

// merge / ganttString / parseQuanta helpers
eq('merge', Sched.merge([{ start: 0, end: 1, label: 'P1', name: 'P1' }, { start: 1, end: 3, label: 'P1', name: 'P1' },
  { start: 3, end: 4, label: 'P2', name: 'P2' }]).map((b) => [b.start, b.end, b.label]), [[0, 3, 'P1'], [3, 4, 'P2']]);
eq('ganttString gap', Sched.ganttString([{ start: 0, end: 2, label: 'P1' }, { start: 4, end: 5, label: 'P2' }]), '0 P1 2 4 P2 5');
eq('parseQuanta', Sched.parseQuanta('4, 8, FCFS'), [4, 8, null]);
eq('parseQuanta all RR', Sched.parseQuanta('2 4'), [2, 4]);

// MLFQ with a finite last level keeps RR there; one-level MLFQ == RR
eq('mlfq [4] == rr 4', stripQ(Sched.run('mlfq', [[0, 24], [0, 3], [0, 3]], { quanta: '4' }).gantt), '0 P1 4 P2 7 P3 10 P1 30');
eq('mlfq [3] == rr 3 (arrival before expired)', stripQ(Sched.run('mlfq', HW2, { quanta: [3] }).gantt),
  Sched.run('rr', HW2, { q: 3 }).gantt);

// bad input is rejected with a readable message
function throws(label, fn, re) {
  try { fn(); check(label, false, 'did not throw'); } catch (e) { check(label, re.test(e.message), e.message); }
}
throws('reject burst 0', () => Sched.run('fcfs', [[0, 0]]), /burst/);
throws('reject negative arrival', () => Sched.run('fcfs', [[-1, 3]]), /arrival/);
throws('reject FCFS in the middle', () => Sched.run('mlfq', [[0, 3]], { quanta: 'FCFS,4' }), /last/);
throws('reject missing priority', () => Sched.run('priority', [[0, 3]]), /priority/);
throws('reject q=0', () => Sched.run('rr', [[0, 3]], { q: 0 }), /Quantum/);
throws('reject unknown algo', () => Sched.run('lottery', [[0, 3]]), /Unknown/);
throws('reject empty list', () => Sched.run('sjf', []), /at least one/);

// every preset reproduces its test case
const caseById = {};
CASES.forEach((c) => { caseById[c.id] = c; });
Sched.PRESETS.forEach((p) => {
  const c = caseById[p.id];
  check('preset ' + p.id + ' has a test case', !!c);
  if (!c) return;
  const r = Sched.run(p.algo, p.procs, p.opts);
  const want = results[c.id];
  eq('preset ' + p.id + ' gantt', r.gantt, want.gantt);
  if (r.kind === 'proc') eq('preset ' + p.id + ' avg WT', r.avg.wt.text, want.avg.wt.text);
  else eq('preset ' + p.id + ' misses', missList(r), missList(want));
});
CASES.forEach((c) => check('case ' + c.id + ' has a preset', Sched.PRESETS.some((p) => p.id === c.id)));

// random inputs: invariants hold for every algorithm and option combination
const examPass = pass, examFail = fail;
let seed = 3511;
const rnd = (n) => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed % n; };
const variants = [
  ['fcfs', {}], ['sjf', {}], ['srtf', { srtfTie: 'keep' }], ['srtf', { srtfTie: 'preempt' }],
  ['rr', { q: 1 }], ['rr', { q: 3, arrivalFirst: false }], ['priority', { preemptive: false }],
  ['priority', { preemptive: true, smallerIsHigher: false }], ['priority-rr', { q: 2 }],
  ['mlfq', { quanta: '2,4,FCFS' }], ['mlfq', { quanta: '3,FCFS', aging: 5 }], ['mlfq', { quanta: '1,2,3' }],
  ['dynamic', { alpha: 1, beta: -1, init: 5, checkEvery: 2 }], ['dynamic', { alpha: 0.5, beta: 2, init: 0, checkEvery: 1, dynTie: 'smaller' }]
];
let fuzzFail = 0;
for (let i = 0; i < 300; i++) {
  const n = 1 + rnd(7);
  const procs = Array.from({ length: n }, () => [rnd(15), 1 + rnd(12), 1 + rnd(4)]);
  variants.forEach(([algo, opts]) => {
    const before = fail;
    invariants('fuzz#' + i + ' ' + algo + JSON.stringify(opts) + JSON.stringify(procs), Sched.run(algo, procs, opts));
    if (fail > before) fuzzFail++;
  });
  const tasks = Array.from({ length: 1 + rnd(4) }, () => { const T = 2 + rnd(9); return [1 + rnd(3), 1 + rnd(T), T]; });
  ['rm', 'edf'].forEach((algo) => ['keepRunning', 'smallerId'].forEach((rtTie) => {
    invariants('fuzz#' + i + ' ' + algo + ' ' + rtTie + JSON.stringify(tasks), Sched.run(algo, tasks, { horizon: 30, rtTie }));
  }));
}

/* ------------------------------------------------------------- report */
console.log('sched.js tests');
console.log('  exam/lecture answers : ' + examPass + ' passed, ' + examFail + ' failed  (' + CASES.length +
  ' cases + ' + Sched.PRESETS.length + ' presets + helpers/validation)');
console.log('  random-input checks  : ' + (pass - examPass) + ' passed, ' + (fail - examFail) + ' failed  (300 inputs x ' +
  (variants.length + 4) + ' algorithm variants)');
console.log(fail ? 'FAIL' : 'ALL PASS');
if (fail) {
  console.log('\nFailures:');
  failures.slice(0, 40).forEach((f) => console.log('  - ' + f));
  if (failures.length > 40) console.log('  ... ' + (failures.length - 40) + ' more');
  process.exitCode = 1;
}
