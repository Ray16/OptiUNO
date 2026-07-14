* GAMS-model hs106.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set i/1*6/;
 Set j/1*8/;
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
objcon.. obj =e= x('1') + 
x('2') + 
x('3');


con1..0.01 * x('5') - 
0.01 * x('8') =g= -1;
con2..0.0025000000000000001 * x('4') - 
0.0025000000000000001 * x('5') - 
0.0025000000000000001 * x('7') =g= -1;
con3..(-0.0025000000000000001) * x('4') - 
0.0025000000000000001 * x('6') =g= -1;
con4..(-100) * x('1') - 
833.33249999999998 * x('4') + 
x('1') * x('6') =g= -83333.330000000002;
con5..1250 * x('4') - 
1250 * x('5') - 
x('2') * x('4') + 
x('2') * x('7') =g= 0;
con6..2500 * x('5') - 
x('3') * x('5') + 
x('3') * x('8') =g= 1250000;
x.lo('1')=100;
x.up('1')=10000;
x.lo('2')=1000;
x.up('2')=10000;
x.lo('3')=1000;
x.up('3')=10000;
x.lo('4')=10;
x.up('4')=1000;
x.lo('6')=10;
x.up('6')=1000;
x.lo('5')=10;
x.up('5')=1000;
x.lo('8')=10;
x.up('8')=1000;
x.lo('7')=10;
x.up('7')=1000;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


