* GAMS-model catena.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*11/;
 Set j/1*32/;
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
con10
con11
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 445.90909090909093 * x('11') + 
445.90909090909093 * x('12') + 
445.90909090909093 * x('13') + 
445.90909090909093 * x('14') + 
445.90909090909093 * x('15') + 
445.90909090909093 * x('16') + 
445.90909090909093 * x('17') + 
445.90909090909093 * x('18') + 
445.90909090909093 * x('19') + 
445.90909090909093 * x('20') + 
222.95454545454547 * x('21');


con1.. power(x('1'), 2) + 
power(x('11'), 2) + 
power(x('22'), 2) =e= 1;
con2.. power(-x('1') + 
x('2'), 2) + 
power(-x('11') + 
x('12'), 2) + 
power(-x('22') + 
x('23'), 2) =e= 1;
con3.. power(-x('2') + 
x('3'), 2) + 
power(-x('12') + 
x('13'), 2) + 
power(-x('23') + 
x('24'), 2) =e= 1;
con4.. power(((- x('10'))) + 6.5999999999999996, 2) + 
power(-x('20') + 
x('21'), 2) + 
power(-x('31') + 
x('32'), 2) =e= 1;
con5.. power(-x('3') + 
x('4'), 2) + 
power(-x('13') + 
x('14'), 2) + 
power(-x('24') + 
x('25'), 2) =e= 1;
con6.. power(-x('4') + 
x('5'), 2) + 
power(-x('14') + 
x('15'), 2) + 
power(-x('25') + 
x('26'), 2) =e= 1;
con7.. power(-x('9') + 
x('10'), 2) + 
power(-x('19') + 
x('20'), 2) + 
power(-x('30') + 
x('31'), 2) =e= 1;
con8.. power(-x('5') + 
x('6'), 2) + 
power(-x('15') + 
x('16'), 2) + 
power(-x('26') + 
x('27'), 2) =e= 1;
con9.. power(-x('6') + 
x('7'), 2) + 
power(-x('16') + 
x('17'), 2) + 
power(-x('27') + 
x('28'), 2) =e= 1;
con10.. power(-x('8') + 
x('9'), 2) + 
power(-x('18') + 
x('19'), 2) + 
power(-x('29') + 
x('30'), 2) =e= 1;
con11.. power(-x('7') + 
x('8'), 2) + 
power(-x('17') + 
x('18'), 2) + 
power(-x('28') + 
x('29'), 2) =e= 1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


