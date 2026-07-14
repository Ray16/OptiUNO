* GAMS-model brownal.dag.gms written by dag2gams Converter at 29/03/2004 16:59:01
* University of Vienna
$offdigit;
 Set j/1*10/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(2 * x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
2 * x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
2 * x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
2 * x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
2 * x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
2 * x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
2 * x('7') + 
x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
2 * x('8') + 
x('9') + 
x('10') - 
11, 2) + 
power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
2 * x('9') + 
x('10') - 
11, 2) + 
power((x('1') * x('2') * x('3') * x('4') * x('5') * x('6') * x('7') * x('8') * x('9') * x('10')) - 1, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


