* GAMS-model hs073.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*4/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 24.550000000000001 * x('1') + 
26.75 * x('2') + 
39 * x('3') + 
40.5 * x('4');


con1.. x('1') + 
x('2') + 
x('3') + 
x('4') =e= 1;
con2..2.2999999999999998 * x('1') + 
5.5999999999999996 * x('2') + 
11.1 * x('3') + 
1.3 * x('4') =g= 5;
con3..(-1.645) * sqrt(0.28000000000000003 * power(x('1'), 2) + 
0.19 * power(x('2'), 2) + 
20.5 * power(x('3'), 2) + 
0.62 * power(x('4'), 2)) + 
12 * x('1') + 
11.9 * x('2') + 
41.799999999999997 * x('3') + 
52.100000000000001 * x('4') =g= 21;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


