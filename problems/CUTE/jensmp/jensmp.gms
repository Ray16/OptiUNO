* GAMS-model jensmp.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(-exp(x('1')) - 
exp(x('2')) + 
4, 2) + 
power(-exp(2 * x('1')) - 
exp(2 * x('2')) + 
6, 2) + 
power(-exp(3 * x('1')) - 
exp(3 * x('2')) + 
8, 2) + 
power(-exp(4 * x('1')) - 
exp(4 * x('2')) + 
10, 2) + 
power(-exp(5 * x('1')) - 
exp(5 * x('2')) + 
12, 2) + 
power(-exp(6 * x('1')) - 
exp(6 * x('2')) + 
14, 2) + 
power(-exp(7 * x('1')) - 
exp(7 * x('2')) + 
16, 2) + 
power(-exp(8 * x('1')) - 
exp(8 * x('2')) + 
18, 2) + 
power(-exp(9 * x('1')) - 
exp(9 * x('2')) + 
20, 2) + 
power(-exp(10 * x('1')) - 
exp(10 * x('2')) + 
22, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


