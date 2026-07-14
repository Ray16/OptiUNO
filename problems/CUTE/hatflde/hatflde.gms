* GAMS-model hatflde.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set j/1*3/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(exp(0.29999999999999999 * x('3')) - 
exp(0.29999999999999999 * x('2')) * x('1') + 
1.5609999999999999, 2) + 
power(exp(0.34999999999999998 * x('3')) - 
exp(0.34999999999999998 * x('2')) * x('1') + 
1.4730000000000001, 2) + 
power(exp(0.40000000000000002 * x('3')) - 
exp(0.40000000000000002 * x('2')) * x('1') + 
1.391, 2) + 
power(exp(0.45000000000000001 * x('3')) - 
exp(0.45000000000000001 * x('2')) * x('1') + 
1.3129999999999999, 2) + 
power(exp(0.5 * x('3')) - 
exp(0.5 * x('2')) * x('1') + 
1.2390000000000001, 2) + 
power(exp(0.55000000000000004 * x('3')) - 
exp(0.55000000000000004 * x('2')) * x('1') + 
1.169, 2) + 
power(exp(0.59999999999999998 * x('3')) - 
exp(0.59999999999999998 * x('2')) * x('1') + 
1.103, 2) + 
power(exp(0.65000000000000002 * x('3')) - 
exp(0.65000000000000002 * x('2')) * x('1') + 
1.04, 2) + 
power(exp(0.69999999999999996 * x('3')) - 
exp(0.69999999999999996 * x('2')) * x('1') + 
0.98099999999999998, 2) + 
power(exp(0.75 * x('3')) - 
exp(0.75 * x('2')) * x('1') + 
0.92500000000000004, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


