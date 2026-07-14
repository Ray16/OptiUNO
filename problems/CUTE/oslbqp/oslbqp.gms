* GAMS-model oslbqp.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set j/1*8/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('1') + 
2 * x('5') - 
x('8') + 
0.5 * power(x('1'), 2) + 
0.5 * power(x('2'), 2) + 
0.5 * power(x('3'), 2) + 
0.5 * power(x('4'), 2) + 
0.5 * power(x('5'), 2) + 
0.5 * power(x('6'), 2) + 
0.5 * power(x('7'), 2) + 
0.5 * power(x('8'), 2);


x.lo('1')=2.5;
x.lo('5')=0.5;
x.up('5')=4;
x.lo('8')=-0;
x.up('8')=4.2999999999999998;
x.lo('7')=-0;
x.lo('6')=-0;
x.lo('2')=-0;
x.up('2')=4.0999999999999996;
x.lo('4')=-0;
x.lo('3')=-0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


