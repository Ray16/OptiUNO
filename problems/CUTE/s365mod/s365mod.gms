* GAMS-model s365mod.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set i/1*7/;
 Set j/1*9/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('1') * x('2');


con1.. sqrt(power(x('2'), 2)) - 
x('9') + 
power(-x('1') + 
x('3'), 2) =e= 0;
con2.. sqrt(power(x('3'), 2)) - 
x('8') + 
power(x('2'), 2) =e= 0;
con3..power(x('4') - 
x('6'), 2) + 
power(x('5') - 
x('7'), 2) =g= 4;
con4..(x('2') * x('4') - 
x('3') * x('5')) / x('8') =g= 1;
con5..(x('2') * x('6') - 
x('3') * x('7')) / x('8') =g= 1;
con6..(x('1') * x('2') - 
x('2') * x('4') + 
x('5') * ((- x('1')) + 
x('3'))) / x('9') =g= 1;
con7..(x('1') * x('2') - 
x('2') * x('6') + 
x('7') * ((- x('1')) + 
x('3'))) / x('9') =g= 1;
x.lo('1')=0.5;
x.lo('2')=0.5;
x.lo('5')=1;
x.lo('7')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


