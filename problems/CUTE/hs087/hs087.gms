* GAMS-model hs087.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*6/;
 Set j/1*11/;
 Equations objcon
con1
con2
con3
con4
con5
con6
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 30 * x('7') + 
31 * x('8') + 
28 * x('9') + 
29 * x('10') + 
30 * x('11');


con1.. x('5') - 
x('9') - 
x('10') - 
x('11') =e= 0;
con2.. x('4') - 
x('7') - 
x('8') =e= 0;
con3.. (-0.0076290453012709987) * sin((- x('3')) + 1.4847699999999999) * x('1') * x('2') + 
0.0068958408297352313 * power(x('1'), 2) =e= -200;
con4.. 0.0076290453012709987 * cos((- x('3')) + 1.4847699999999999) * x('1') * x('2') + 
x('4') - 
0.00065650056189229318 * power(x('1'), 2) =e= 300;
con5.. 0.0076290453012709987 * sin(x('3') + 1.4847699999999999) * x('1') * x('2') + 
x('6') - 
0.0068958408297352313 * power(x('2'), 2) =e= 0;
con6.. 0.0076290453012709987 * cos(x('3') + 1.4847699999999999) * x('1') * x('2') + 
x('5') - 
0.00065650056189229318 * power(x('2'), 2) =e= 0;
x.lo('1')=340;
x.up('1')=420;
x.lo('2')=340;
x.up('2')=420;
x.lo('3')=0;
x.up('3')=0.52359999999999995;
x.lo('4')=0;
x.up('4')=400;
x.lo('5')=0;
x.up('5')=1000;
x.lo('6')=-1000;
x.up('6')=1000;
x.up('7')=300;
x.lo('8')=0;
x.up('9')=100;
x.lo('10')=0;
x.up('10')=100;
x.lo('11')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


