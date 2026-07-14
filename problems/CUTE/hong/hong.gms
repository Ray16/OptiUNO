* GAMS-model hong.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*4/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.080000000000000002 * exp(9.5 * x('1')) + 
3.9500000000000002 * exp(5.5 * x('2')) + 
0.89000000000000001 * exp(7 * x('4')) + 
1657834 * exp((-5.9199999999999999) * x('3') - 13.32) - 3.5800000000000005;


con1.. x('1') + 
x('2') + 
x('3') + 
x('4') =e= 1;
x.lo('1')=0;
x.up('1')=1;
x.lo('2')=0;
x.up('2')=1;
x.lo('3')=0;
x.up('3')=1;
x.lo('4')=0;
x.up('4')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


