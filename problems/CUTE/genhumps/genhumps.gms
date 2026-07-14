* GAMS-model genhumps.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set j/1*5/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(sin(2 * x('2')), 2) * power(sin(2 * x('3')), 2) + 
power(sin(2 * x('3')), 2) * power(sin(2 * x('4')), 2) + 
power(sin(2 * x('4')), 2) * power(sin(2 * x('5')), 2) + 
power(sin(2 * x('1')), 2) * power(sin(2 * x('2')), 2) + 
0.050000000000000003 * power(x('1'), 2) + 
0.10000000000000001 * power(x('2'), 2) + 
0.10000000000000001 * power(x('3'), 2) + 
0.10000000000000001 * power(x('4'), 2) + 
0.050000000000000003 * power(x('5'), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


