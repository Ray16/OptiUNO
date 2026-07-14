* GAMS-model rosenmmx.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*4/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
con4
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('5');


con1..15 * x('1') - 
15 * x('2') - 
21 * x('3') - 
3 * x('4') - 
x('5') + 
11 * power(x('1'), 2) + 
11 * power(x('2'), 2) + 
power(x('4'), 2) + 
12 * power(x('3'), 2) =l= 50;
con2..(-5) * x('1') - 
5 * x('2') - 
21 * x('3') + 
7 * x('4') - 
x('5') + 
power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('4'), 2) + 
2 * power(x('3'), 2) =l= 0;
con3..(-15) * x('1') - 
5 * x('2') - 
21 * x('3') - 
3 * x('4') - 
x('5') + 
11 * power(x('1'), 2) + 
21 * power(x('2'), 2) + 
21 * power(x('4'), 2) + 
12 * power(x('3'), 2) =l= 100;
con4..5 * x('1') - 
15 * x('2') - 
11 * x('3') - 
3 * x('4') - 
x('5') + 
11 * power(x('1'), 2) + 
11 * power(x('2'), 2) + 
11 * power(x('4'), 2) + 
12 * power(x('3'), 2) =l= 80;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


