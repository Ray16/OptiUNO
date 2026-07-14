* GAMS-model twobars.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*2/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= sqrt(power(x('2'), 2) + 1) * x('1');


con1..sqrt(power(x('2'), 2) + 1) * (8 * (1/x('1')) - 
1/(x('1') * x('2'))) =l= 8.0645161290322598;
con2..sqrt(power(x('2'), 2) + 1) * (8 * (1/x('1')) + 
1/(x('1') * x('2'))) =l= 8.0645161290322598;
x.lo('1')=0.20000000000000001;
x.up('1')=4;
x.lo('2')=0.10000000000000001;
x.up('2')=1.6000000000000001;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


