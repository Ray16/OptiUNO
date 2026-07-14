* GAMS-model lsqfit.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*2/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.5 * power(0.10000000000000001 * x('1') + 
x('2') - 
0.25, 2) + 
0.5 * power(0.29999999999999999 * x('1') + 
x('2') - 
0.29999999999999999, 2) + 
0.5 * power(0.5 * x('1') + 
x('2') - 
0.625, 2) + 
0.5 * power(0.69999999999999996 * x('1') + 
x('2') - 
0.70099999999999996, 2) + 
0.5 * power(0.90000000000000002 * x('1') + 
x('2') - 
1, 2);


con1..x('1') + 
x('2') =l= 0.84999999999999998;
x.lo('1')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


