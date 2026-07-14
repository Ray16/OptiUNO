* GAMS-model hs268.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*5/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
con4
con5
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 18340 * x('1') - 
34198 * x('2') + 
4542 * x('3') + 
8672 * x('4') + 
86 * x('5') + 
20909 * power(x('2'), 2) + 
1755 * power(x('3'), 2) + 
1515 * power(x('4'), 2) + 
27 * power(x('5'), 2) + 
10197 * power(x('1'), 2) - 
24908 * x('1') * x('2') - 
2026 * x('1') * x('3') + 
3896 * x('1') * x('4') + 
658 * x('1') * x('5') - 
3466 * x('2') * x('3') - 
9828 * x('2') * x('4') - 
372 * x('2') * x('5') + 
2178 * x('3') * x('4') - 
348 * x('3') * x('5') - 
44 * x('4') * x('5') + 14463;


con1..(-4) * x('1') - 
2 * x('2') + 
3 * x('3') - 
5 * x('4') + 
x('5') =g= -30;
con2..8 * x('1') - 
x('2') + 
2 * x('3') + 
5 * x('4') - 
3 * x('5') =g= 11;
con3..(-8) * x('1') + 
x('2') - 
2 * x('3') - 
5 * x('4') + 
3 * x('5') =g= -40;
con4..10 * x('1') + 
10 * x('2') - 
3 * x('3') + 
5 * x('4') + 
4 * x('5') =g= 20;
con5..-x('1') - 
x('2') - 
x('3') - 
x('4') - 
x('5') =g= -5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


