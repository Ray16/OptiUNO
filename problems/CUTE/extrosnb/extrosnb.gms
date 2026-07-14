* GAMS-model extrosnb.dag.gms written by dag2gams Converter at 29/03/2004 16:59:01
* University of Vienna
$offdigit;
 Set j/1*10/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('1')) - 1, 2) + 
100 * power(x('2') - 
power(x('1'), 2), 2) + 
100 * power(x('3') - 
power(x('2'), 2), 2) + 
100 * power(x('4') - 
power(x('3'), 2), 2) + 
100 * power(x('5') - 
power(x('4'), 2), 2) + 
100 * power(x('6') - 
power(x('5'), 2), 2) + 
100 * power(x('7') - 
power(x('6'), 2), 2) + 
100 * power(x('8') - 
power(x('7'), 2), 2) + 
100 * power(x('9') - 
power(x('8'), 2), 2) + 
100 * power(x('10') - 
power(x('9'), 2), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


