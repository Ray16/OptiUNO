* GAMS-model aircrfta.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
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
objcon.. obj =e= 0;


con1.. (-3.9329999999999998) * x('1') + 
0.107 * x('2') + 
0.126 * x('3') - 
9.9900000000000002 * x('5') - 
0.72699999999999998 * x('2') * x('3') + 
63.5 * x('2') * x('4') + 
8.3900000000000006 * x('3') * x('4') - 
684.39999999999998 * x('4') * x('5') =e= 0;
con2.. -x('3') - 
0.19600000000000001 * x('5') + 
x('1') * x('4') =e= 0;
con3.. x('2') - 
x('4') - 
x('1') * x('5') =e= 0.1168;
con4.. 0.002 * x('1') - 
0.23499999999999999 * x('3') + 
5.6699999999999999 * x('5') - 
0.71599999999999997 * x('1') * x('2') - 
1.5780000000000001 * x('1') * x('4') + 
1.1319999999999999 * x('2') * x('4') =e= 0;
con5.. (-0.98699999999999999) * x('2') - 
22.949999999999999 * x('4') + 
0.94899999999999995 * x('1') * x('3') + 
0.17299999999999999 * x('1') * x('5') =e= 2.8370000000000002;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


