* GAMS-model dixon3dq.dag.gms written by dag2gams Converter at 29/03/2004 16:59:01
* University of Vienna
$offdigit;
 Set j/1*10/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('1')) - 1, 2) + 
power((x('10')) - 1, 2) + 
power(x('2') - 
x('3'), 2) + 
power(x('3') - 
x('4'), 2) + 
power(x('4') - 
x('5'), 2) + 
power(x('5') - 
x('6'), 2) + 
power(x('6') - 
x('7'), 2) + 
power(x('7') - 
x('8'), 2) + 
power(x('8') - 
x('9'), 2) + 
power(x('9') - 
x('10'), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


