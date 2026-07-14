* GAMS-model lewispol.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*9/;
 Set j/1*6/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) + 
power(x('4'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2);


con1.. 4 * x('3') + 
9 * x('4') + 
16 * x('5') + 
25 * x('6') =e= -30;
con2.. x('2') + 
2 * x('3') + 
3 * x('4') + 
4 * x('5') + 
5 * x('6') =e= -6;
con3.. x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') =e= -1;
con4.. (-0.0001) * x('6') + 
0.0001 * power(x('6'), 3) =e= 0;
con5.. (-0.0001) * x('1') + 
0.0001 * power(x('1'), 3) =e= 0;
con6.. (-0.0001) * x('5') + 
0.0001 * power(x('5'), 3) =e= 0;
con7.. (-0.0001) * x('4') + 
0.0001 * power(x('4'), 3) =e= 0;
con8.. (-0.0001) * x('3') + 
0.0001 * power(x('3'), 3) =e= 0;
con9.. (-0.0001) * x('2') + 
0.0001 * power(x('2'), 3) =e= 0;
x.lo('1')=-10;
x.up('1')=10;
x.lo('2')=-10;
x.up('2')=10;
x.lo('3')=-10;
x.up('3')=10;
x.lo('4')=-10;
x.up('4')=10;
x.lo('5')=-10;
x.up('5')=10;
x.lo('6')=-10;
x.up('6')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


