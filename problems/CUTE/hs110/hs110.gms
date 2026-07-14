* GAMS-model hs110.dag.gms written by dag2gams Converter at 29/03/2004 16:59:01
* University of Vienna
$offdigit;
 Set j/1*10/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(log(x('1') - 2), 2) + 
power(log((- x('1')) + 10), 2) + 
power(log(x('2') - 2), 2) + 
power(log((- x('2')) + 10), 2) + 
power(log(x('3') - 2), 2) + 
power(log((- x('3')) + 10), 2) + 
power(log(x('4') - 2), 2) + 
power(log((- x('4')) + 10), 2) + 
power(log(x('5') - 2), 2) + 
power(log((- x('5')) + 10), 2) + 
power(log(x('6') - 2), 2) + 
power(log((- x('6')) + 10), 2) + 
power(log(x('7') - 2), 2) + 
power(log((- x('7')) + 10), 2) + 
power(log(x('8') - 2), 2) + 
power(log((- x('8')) + 10), 2) + 
power(log(x('9') - 2), 2) + 
power(log((- x('9')) + 10), 2) + 
power(log(x('10') - 2), 2) + 
power(log((- x('10')) + 10), 2) - 
(x('1') * x('2') * x('3') * x('4') * x('5') * x('6') * x('7') * x('8') * x('9') * x('10'))**(0.20000000000000001);


x.lo('1')=2.0009999999999999;
x.up('1')=9.9990000000000006;
x.lo('2')=2.0009999999999999;
x.up('2')=9.9990000000000006;
x.lo('3')=2.0009999999999999;
x.up('3')=9.9990000000000006;
x.lo('4')=2.0009999999999999;
x.up('4')=9.9990000000000006;
x.lo('5')=2.0009999999999999;
x.up('5')=9.9990000000000006;
x.lo('6')=2.0009999999999999;
x.up('6')=9.9990000000000006;
x.lo('7')=2.0009999999999999;
x.up('7')=9.9990000000000006;
x.lo('8')=2.0009999999999999;
x.up('8')=9.9990000000000006;
x.lo('9')=2.0009999999999999;
x.up('9')=9.9990000000000006;
x.lo('10')=2.0009999999999999;
x.up('10')=9.9990000000000006;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


