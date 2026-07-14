* GAMS-model hs055.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*6/;
 Set j/1*6/;
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
objcon.. obj =e= exp(x('1') * x('2')) + 
x('1') + 
2 * x('3') + 
4 * x('5');


con1.. x('4') + 
x('6') =e= 2;
con2.. x('3') + 
x('5') =e= 2;
con3.. x('1') + 
x('2') =e= 1;
con4.. x('2') + 
x('5') + 
x('6') =e= 2;
con5.. x('1') + 
x('3') + 
x('4') =e= 3;
con6.. x('1') + 
2 * x('3') + 
5 * x('5') =e= 6;
x.lo('1')=0;
x.up('1')=1;
x.lo('2')=0;
x.up('2')=1;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
x.lo('6')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


