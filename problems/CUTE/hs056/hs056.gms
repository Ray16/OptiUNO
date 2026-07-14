* GAMS-model hs056.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*4/;
 Set j/1*7/;
 Equations objcon
con1
con2
con3
con4
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(x('5') * x('6') * x('7'));


con1.. (-7.2000000000000002) * power(sin(x('4')), 2) + 
x('5') + 
2 * x('6') + 
2 * x('7') =e= 0;
con2.. (-4.2000000000000002) * power(sin(x('1')), 2) + 
x('5') =e= 0;
con3.. (-4.2000000000000002) * power(sin(x('3')), 2) + 
x('7') =e= 0;
con4.. (-4.2000000000000002) * power(sin(x('2')), 2) + 
x('6') =e= 0;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
x.lo('6')=0;
x.lo('7')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


