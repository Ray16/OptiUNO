* GAMS-model hs080.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= exp(x('1') * x('2') * x('3') * x('4') * x('5'));


con1.. power(x('1'), 3) + 
power(x('2'), 3) =e= -1;
con2.. power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) + 
power(x('4'), 2) + 
power(x('5'), 2) =e= 10;
con3.. x('2') * x('3') - 
5 * x('4') * x('5') =e= 0;
x.lo('1')=-2.2999999999999998;
x.up('1')=2.2999999999999998;
x.lo('2')=-2.2999999999999998;
x.up('2')=2.2999999999999998;
x.lo('3')=-3.2000000000000002;
x.up('3')=3.2000000000000002;
x.lo('4')=-3.2000000000000002;
x.up('4')=3.2000000000000002;
x.lo('5')=-3.2000000000000002;
x.up('5')=3.2000000000000002;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


