// Check that the site's simulator reproduces the official Spring 2023 priority+RR Gantt chart (q = 2)
// using a process table reconstructed from that chart.
const Sched = require('C:/Code/UST/COMP3511/Midterm_Site/assets/sched.js');
const procs = [
  { arrival: 0, burst: 5, priority: 2 },  // P1
  { arrival: 1, burst: 3, priority: 1 },  // P2
  { arrival: 2, burst: 8, priority: 2 },  // P3
  { arrival: 8, burst: 2, priority: 1 },  // P4
  { arrival: 9, burst: 6, priority: 2 },  // P5
];
const r = Sched.run('priority-rr', procs, { q: 2, smallerIsHigher: true });
const official = '0 P1 1 P2 4 P1 5 P3 7 P1 8 P4 10 P1 11 P3 13 P5 15 P1 16 P3 18 P5 20 P3 22 P5 24';
console.log('sim     :', r.gantt);
console.log('official:', official);
console.log(r.gantt === official ? 'MATCH' : 'DIFFERENT');
console.log('avg WT  :', r.avg.wt.text);
