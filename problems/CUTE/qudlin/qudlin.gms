* GAMS-model qudlin.dag.gms written by dag2gams Converter at 29/03/2004 16:59:02
* University of Vienna
$offdigit;
 Set j/1*12/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-10) * x('1') - 
20 * x('2') - 
30 * x('3') - 
40 * x('4') - 
50 * x('5') - 
60 * x('6') - 
70 * x('7') - 
80 * x('8') - 
90 * x('9') - 
100 * x('10') - 
110 * x('11') - 
120 * x('12') + 
x('1') * x('2') + 
x('2') * x('3') + 
x('3') * x('4') + 
x('4') * x('5') + 
x('5') * x('6') + 
x('6') * x('7');


x.lo('1')=0;
x.up('1')=10;
x.lo('2')=0;
x.up('2')=10;
x.lo('3')=0;
x.up('3')=10;
x.lo('4')=0;
x.up('4')=10;
x.lo('5')=0;
x.up('5')=10;
x.lo('6')=0;
x.up('6')=10;
x.lo('7')=0;
x.up('7')=10;
x.lo('8')=0;
x.up('8')=10;
x.lo('9')=0;
x.up('9')=10;
x.lo('10')=0;
x.up('10')=10;
x.lo('11')=0;
x.up('11')=10;
x.lo('12')=0;
x.up('12')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


