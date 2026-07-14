* GAMS-model hs045.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set j/1*5/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -0.0083333333333333332*(x('1') * x('2') * x('3') * x('4') * x('5')) + 2;


x.lo('1')=0;
x.up('1')=1;
x.lo('2')=0;
x.up('2')=2;
x.lo('3')=0;
x.up('3')=3;
x.lo('4')=0;
x.up('4')=4;
x.lo('5')=0;
x.up('5')=5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


