* GAMS-model genhs28.dag.gms written by dag2gams Converter at 29/03/2004 16:59:02
* University of Vienna
$offdigit;
 Set i/1*8/;
 Set j/1*10/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('1') + 
x('2'), 2) + 
power(x('2') + 
x('3'), 2) + 
power(x('3') + 
x('4'), 2) + 
power(x('4') + 
x('5'), 2) + 
power(x('5') + 
x('6'), 2) + 
power(x('6') + 
x('7'), 2) + 
power(x('7') + 
x('8'), 2) + 
power(x('8') + 
x('9'), 2) + 
power(x('9') + 
x('10'), 2);


con1.. x('8') + 
2 * x('9') + 
3 * x('10') =e= 1;
con2.. x('7') + 
2 * x('8') + 
3 * x('9') =e= 1;
con3.. x('6') + 
2 * x('7') + 
3 * x('8') =e= 1;
con4.. x('5') + 
2 * x('6') + 
3 * x('7') =e= 1;
con5.. x('4') + 
2 * x('5') + 
3 * x('6') =e= 1;
con6.. x('3') + 
2 * x('4') + 
3 * x('5') =e= 1;
con7.. x('2') + 
2 * x('3') + 
3 * x('4') =e= 1;
con8.. x('1') + 
2 * x('2') + 
3 * x('3') =e= 1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


