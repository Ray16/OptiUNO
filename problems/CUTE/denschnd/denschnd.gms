* GAMS-model denschnd.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set j/1*3/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(2 * x('1') * x('2') + 
x('1') * x('3') - 
3 * x('2') * x('3'), 2) + 
power(2 * x('1') * x('2') * x('3'), 2) + 
power(power(x('1'), 2) + 
power(x('2'), 3) - 
power(x('3'), 4), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


