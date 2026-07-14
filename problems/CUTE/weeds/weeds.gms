* GAMS-model weeds.dag.gms written by dag2gams Converter at 29/03/2004 16:59:06
* University of Vienna
$offdigit;
 Set i/1*12/;
 Set j/1*15/;
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
con12
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(((- x('1') / (x('4') + 
1))) + 5.3079999999999998, 2) + 
power(((- x('1') / (x('5') + 
1))) + 7.2400000000000002, 2) + 
power(((- x('1') / (x('6') + 
1))) + 9.6379999999999999, 2) + 
power(((- x('1') / (x('7') + 
1))) + 12.866, 2) + 
power(((- x('1') / (x('8') + 
1))) + 17.068999999999999, 2) + 
power(((- x('1') / (x('9') + 
1))) + 23.192, 2) + 
power(((- x('1') / (x('10') + 
1))) + 31.443000000000001, 2) + 
power(((- x('1') / (x('11') + 
1))) + 38.558, 2) + 
power(((- x('1') / (x('12') + 
1))) + 50.155999999999999, 2) + 
power(((- x('1') / (x('13') + 
1))) + 62.948, 2) + 
power(((- x('1') / (x('14') + 
1))) + 75.995000000000005, 2) + 
power(((- x('1') / (x('15') + 
1))) + 91.971999999999994, 2);


con1.. exp((- (x('2') + 
12 * x('3')))) - 
x('15') =e= 0;
con2.. exp((- (x('2') + 
11 * x('3')))) - 
x('14') =e= 0;
con3.. exp((- (x('2') + 
10 * x('3')))) - 
x('13') =e= 0;
con4.. exp((- (x('2') + 
9 * x('3')))) - 
x('12') =e= 0;
con5.. exp((- (x('2') + 
8 * x('3')))) - 
x('11') =e= 0;
con6.. exp((- (x('2') + 
7 * x('3')))) - 
x('10') =e= 0;
con7.. exp((- (x('2') + 
6 * x('3')))) - 
x('9') =e= 0;
con8.. exp((- (x('2') + 
5 * x('3')))) - 
x('8') =e= 0;
con9.. exp((- (x('2') + 
4 * x('3')))) - 
x('7') =e= 0;
con10.. exp((- (x('2') + 
3 * x('3')))) - 
x('6') =e= 0;
con11.. exp((- (x('2') + 
2 * x('3')))) - 
x('5') =e= 0;
con12.. exp((- (x('2') + 
x('3')))) - 
x('4') =e= 0;
x.up('3')=3;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


