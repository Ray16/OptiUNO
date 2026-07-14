* GAMS-model robot.dag.gms written by dag2gams Converter at 29/03/2004 16:59:05
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*14/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('1') - 
x('8'), 2) + 
power(x('2') - 
x('9'), 2) + 
power(x('3') - 
x('10'), 2) + 
power(x('4') - 
x('11'), 2) + 
power(x('5') - 
x('12'), 2) + 
power(x('6') - 
x('13'), 2) + 
power(x('7') - 
x('14'), 2);


con1.. cos(x('1')) + 
cos(x('2')) + 
cos(x('3')) + 
cos(x('4')) + 
cos(x('5')) + 
cos(x('6')) + 
0.5 * cos(x('7')) =e= 4;
con2.. sin(x('1')) + 
sin(x('2')) + 
sin(x('3')) + 
sin(x('4')) + 
sin(x('5')) + 
sin(x('6')) + 
0.5 * sin(x('7')) =e= 4;
x.lo('8')=-0;
x.up('8')=0;
x.lo('9')=-0;
x.up('9')=0;
x.lo('10')=-0;
x.up('10')=0;
x.lo('11')=-0;
x.up('11')=0;
x.lo('12')=-0;
x.up('12')=0;
x.lo('13')=-0;
x.up('13')=0;
x.lo('14')=-0;
x.up('14')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


