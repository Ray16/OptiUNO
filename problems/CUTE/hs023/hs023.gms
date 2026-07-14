* GAMS-model hs023.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*5/;
 Set j/1*2/;
 Equations objcon
con1
con2
con3
con4
con5
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('1'), 2) + 
power(x('2'), 2);


con1..x('1') + 
x('2') =g= 1;
con2..power(x('1'), 2) + 
power(x('2'), 2) =g= 1;
con3..-x('1') + 
power(x('2'), 2) =g= 0;
con4..-x('2') + 
power(x('1'), 2) =g= 0;
con5..9 * power(x('1'), 2) + 
power(x('2'), 2) =g= 9;
x.lo('1')=-50;
x.up('1')=50;
x.lo('2')=-50;
x.up('2')=50;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


