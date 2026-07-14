* GAMS-model hs059.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*2/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 28.106000000000002 * (1/(x('2') + 
1)) + 
2.8673000000000002 * exp(0.00050000000000000001 * x('1') * x('2')) + 
3.8111999999999999 * x('1') + 
6.8305999999999996 * x('2') - 
0.12694 * power(x('1'), 2) - 
0.25645000000000001 * power(x('2'), 2) - 
0.030234 * x('1') * x('2') + 
0.0020566999999999998 * power(x('1'), 3) + 
0.0034604000000000002 * power(x('2'), 3) + 
0.00128134 * x('2') * power(x('1'), 2) - 
0.00034049999999999998 * x('1') * power(x('2'), 2) - 
1.0345e-05 * power(x('1'), 4) - 
1.3514e-05 * power(x('2'), 4) + 
5.2375000000000003e-06 * power(x('1'), 2) * power(x('2'), 2) + 
1.6638000000000001e-06 * x('1') * power(x('2'), 3) - 
3.5256000000000003e-05 * x('2') * power(x('1'), 3) + 
2.266e-07 * x('2') * power(x('1'), 4) + 
6.2999999999999995e-08 * power(x('2'), 2) * power(x('1'), 3) - 
6.9999999999999996e-10 * power(x('2'), 3) * power(x('1'), 3) - 75.195999999999998;


con1..(-5) * x('1') + 
power((x('2')) - 50, 2) =g= -275;
con2..x('2') - 
0.0080000000000000002 * power(x('1'), 2) =g= 0;
con3..x('1') * x('2') =g= 700;
x.lo('1')=0;
x.up('1')=75;
x.lo('2')=0;
x.up('2')=65;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


