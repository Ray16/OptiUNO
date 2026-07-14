* GAMS-model hs071.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*4/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('3') + 
x('1') * x('4') * (x('1') + 
x('2') + 
x('3'));


con1.. power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) + 
power(x('4'), 2) =e= 40;
con2..x('1') * x('2') * x('3') * x('4') =g= 25;
x.lo('1')=1;
x.up('1')=5;
x.lo('2')=1;
x.up('2')=5;
x.lo('3')=1;
x.up('3')=5;
x.lo('4')=1;
x.up('4')=5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


