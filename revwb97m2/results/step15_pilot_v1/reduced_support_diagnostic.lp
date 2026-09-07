\ Model COACH_C0_R2
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 [ 2 weighted_residual[0] ^2 + 2 weighted_residual[1] ^2
   + 2 weighted_residual[2] ^2 + 2 weighted_residual[3] ^2
   + 2 weighted_residual[4] ^2 + 2 weighted_residual[5] ^2
   + 2 weighted_residual[6] ^2 + 2 weighted_residual[7] ^2
   + 2 weighted_residual[8] ^2 + 2 weighted_residual[9] ^2
   + 2 weighted_residual[10] ^2 + 2 weighted_residual[11] ^2
   + 2 weighted_residual[12] ^2 + 2 weighted_residual[13] ^2
   + 2 weighted_residual[14] ^2 + 2 weighted_residual[15] ^2
   + 2 weighted_residual[16] ^2 + 2 weighted_residual[17] ^2
   + 2 weighted_residual[18] ^2 + 2 weighted_residual[19] ^2 ] / 2 
Subject To
 R0: beta[0] - 25 selected[0] <= 0
 R1: beta[0] + 25 selected[0] >= 0
 R2: beta[8] - 25 selected[8] <= 0
 R3: beta[8] + 25 selected[8] >= 0
 R4: beta[96] - 25 selected[96] <= 0
 R5: beta[96] + 25 selected[96] >= 0
 R6: beta[104] - 25 selected[104] <= 0
 R7: beta[104] + 25 selected[104] >= 0
 R8: beta[192] - 25 selected[192] <= 0
 R9: beta[192] + 25 selected[192] >= 0
 R10: beta[200] - 25 selected[200] <= 0
 R11: beta[200] + 25 selected[200] >= 0
 R12: beta[288] - 25 selected[288] <= 0
 R13: beta[288] + 25 selected[288] >= 0
 R14: beta[289] - 25 selected[289] <= 0
 R15: beta[289] + 25 selected[289] >= 0
 R16: beta[290] - 25 selected[290] <= 0
 R17: beta[290] + 25 selected[290] >= 0
 R18: beta[291] - 25 selected[291] <= 0
 R19: beta[291] + 25 selected[291] >= 0
 R20: selected[288] = 1
 R21: selected[289] = 1
 R22: selected[290] = 1
 R23: selected[291] = 1
 support_budget: selected[0] + selected[8] + selected[96] + selected[104]
   + selected[192] + selected[200] + selected[288] + selected[289]
   + selected[290] + selected[291] <= 7
 UEG_exchange: beta[0] + beta[288] = 1
 R26: - 0.2522016449708661 beta[0] + 0.1838898055741412 beta[8]
   + 0.0116581467647352 beta[96] + 4.20098e-05 beta[104]
   - 0.00311292910454243 beta[192] - 0.00845288273770085 beta[200]
   - 0.2921209532227276 beta[288] + 5.3847042806377549e-04 beta[289]
   - 0.015956572064799 beta[290] - 4.9866e-09 beta[291]
   + weighted_residual[0] = -0.290127464393108
 R27: - 0.2216728194322263 beta[0] + 0.0914860448807573 beta[8]
   - 0.00721272616536586 beta[96] + 0.00452282756894152 beta[104]
   - 0.0301724466519035 beta[192] - 0.00797554522648072 beta[200]
   - 0.29858205666189 beta[288] + 8.65867e-05 beta[289]
   + 0.0680054197263078 beta[290] + 7.38144e-11 beta[291]
   + weighted_residual[1] = -0.2625450743804912
 R28: - 0.2533759945949692 beta[0] + 0.1183251012626602 beta[8]
   + 0.00960975432776205 beta[96] + 0.00157823777618981 beta[104]
   - 0.00288972697340022 beta[192] - 0.00504450833922073 beta[200]
   - 0.31797074561487 beta[288] + 0.000358772 beta[289]
   + 0.073940998287532 beta[290] - 4.69783e-09 beta[291]
   + weighted_residual[2] = -0.267568911653786
 R29: - 0.00136255339832303 beta[0] - 5.3074831875221662e-04 beta[8]
   - 2.11861e-05 beta[96] + 1.70521e-05 beta[104] - 3.80053e-05 beta[192]
   + 1.61071e-06 beta[200] - 0.00175061600003801 beta[288]
   - 4e-08 beta[289] + 0.000641999 beta[290] + weighted_residual[3]
   = -0.00133795200133561
 R30: 0.00304410179879255 beta[0] - 0.00303054959861271 beta[8]
   - 1.7408615448216702e-04 beta[96] - 3.26564e-05 beta[104]
   + 0.00032339 beta[192] + 1.8321478483449005e-04 beta[200]
   + 0.00515173600003749 beta[288] - 4.94e-06 beta[289]
   - 0.00171294 beta[290] + weighted_residual[4] = 0.00382116400033976
 R31: - 0.00106514672033597 beta[0] + 0.00404764299631211 beta[8]
   + 0.00042584 beta[96] - 2.6102133013447548e-04 beta[104]
   - 4.45264e-05 beta[192] - 9.3509618371040437e-04 beta[200]
   - 0.00255564 beta[288] + 4.2384e-05 beta[289]
   - 3.8132332238413613e-04 beta[290] + weighted_residual[5]
   = -0.00207569200072158
 R32: - 0.0310841591967489 beta[0] + 0.0118419393409205 beta[8]
   + 0.000257238 beta[96] + 0.0011169207053201 beta[104]
   - 9.2850313616396998e-04 beta[192] - 9.656675095916701e-04 beta[200]
   - 0.0308092341973545 beta[288] + 9.0790576155465829e-04 beta[289]
   - 0.00647266 beta[290] - 1.06863e-05 beta[291] + weighted_residual[6]
   = -0.0304445613613824
 R33: - 0.0314345230395576 beta[0] + 0.00956036891444131 beta[8]
   - 3.2512669147933187e-04 beta[96] + 8.4727011499974888e-04 beta[104]
   - 0.0013404822764905 beta[192] - 7.7470188005640561e-04 beta[200]
   - 0.0309571697714706 beta[288] + 5.4476116659117732e-04 beta[289]
   - 0.00399619633605032 beta[290] - 7.7986e-06 beta[291]
   + weighted_residual[7] = -0.0306944805753814
 R34: - 0.00517212350451533 beta[0] + 0.034375826045571 beta[8]
   + 0.00411970932501557 beta[96] + 0.00178797747349269 beta[104]
   + 0.00140172700340351 beta[192] - 0.00172273874803701 beta[200]
   - 0.003857152862425 beta[288] + 7.9803343098507615e-04 beta[289]
   - 0.00718182458841103 beta[290] + 8.53609e-07 beta[291]
   + weighted_residual[8] = -0.00817197788843361
 R35: - 0.0457860663424818 beta[0] - 0.0480656257569154 beta[8]
   + 0.00266829498304423 beta[96] + 0.00976130495445724 beta[104]
   - 1.9303561188292823e-04 beta[192] - 0.0030045531231673 beta[200]
   - 0.0412950643056124 beta[288] + 0.00155259011681048 beta[289]
   + 0.0113659161072361 beta[290] + 5.36176e-07 beta[291]
   + weighted_residual[9] = -0.0323708096285408
 R36: 0.00151385599922702 beta[0] - 0.00636970468916161 beta[8]
   + 0.010289039912553 beta[96] + 0.0118501841712516 beta[104]
   + 0.00488248552159539 beta[192] - 0.00343768392591812 beta[200]
   + 0.0056716950065746 beta[288] + 0.00240559706858647 beta[289]
   + 0.0143277926311958 beta[290] + 5.02603e-06 beta[291]
   + weighted_residual[10] = 0.0171719495869786
 R37: 0.0637298748269426 beta[0] + 0.0459006792344303 beta[8]
   + 0.00786884823123726 beta[96] - 0.000914883 beta[104]
   + 0.00531047537195336 beta[192] - 5.5378438077829419e-04 beta[200]
   + 0.0570158454763971 beta[288] + 6.8067837228926787e-04 beta[289]
   + 0.00997484725313472 beta[290] + 8.88976e-09 beta[291]
   + weighted_residual[11] = 0.0652133222435025
 R38: 0.0420718751251958 beta[0] + 0.0281686114340684 beta[8]
   + 0.00628817583131219 beta[96] - 0.00100483741616053 beta[104]
   + 0.00405186617889774 beta[192] - 5.3413422697446626e-04 beta[200]
   + 0.0392479270918885 beta[288] + 6.8215475354088196e-04 beta[289]
   + 0.00674770796110305 beta[290] - 2.59383e-06 beta[291]
   + weighted_residual[12] = 0.0451783019337006
 R39: - 0.0448156566466839 beta[0] - 0.1077167402685063 beta[8]
   - 0.0233736554365823 beta[96] - 9.5602712692805273e-04 beta[104]
   - 0.012427472124579 beta[192] + 0.00612927893370446 beta[200]
   - 0.0226220304974003 beta[288] - 0.00574275708914975 beta[289]
   - 0.0421736056107895 beta[290] + 2.95978e-07 beta[291]
   + weighted_residual[13] = -0.0585380816632672
 R40: 0.00404734030029669 beta[0] - 0.0213757691396352 beta[8]
   - 0.00859628277153288 beta[96] - 0.00238779781623927 beta[104]
   - 0.00389934518277807 beta[192] + 0.0035294543031706 beta[200]
   + 0.00917241390034642 beta[288] - 0.00490158778968065 beta[289]
   - 0.0202565684354302 beta[290] + 2.56064e-07 beta[291]
   + weighted_residual[14] = -0.00859389399891641
 R41: - 0.0936400833353675 beta[0] - 0.00371812751447107 beta[8]
   - 0.0095517681617651 beta[96] + 0.00143694322749072 beta[104]
   - 0.022889505051034 beta[192] + 0.00904481275476884 beta[200]
   - 0.0775469772918346 beta[288] + 0.00276404449569422 beta[289]
   - 0.0201606148893171 beta[290] + weighted_residual[15]
   = -0.1160977672264934
 R42: - 0.1201372699334516 beta[0] + 0.0457642841578326 beta[8]
   - 0.00692837630813633 beta[96] + 2.9190184324258026e-04 beta[104]
   - 0.024028871971514 beta[192] + 0.00490670547294603 beta[200]
   - 0.1178540361261741 beta[288] + 0.00309079183408369 beta[289]
   - 0.0255279227953956 beta[290] + weighted_residual[16]
   = -0.1574379255457141
 R43: - 0.0299961359451209 beta[0] + 0.0299961359451211 beta[8]
   - 0.0321885369996884 beta[192] + 3.9231239592620758e-04 beta[200]
   - 0.0363689179480715 beta[288] - 3.79118e-05 beta[289]
   - 0.0344420572097808 beta[290] + weighted_residual[17]
   = -0.0705225901836497
 R44: - 0.0282117383349266 beta[0] - 0.0760821470055402 beta[8]
   - 0.0134229742996163 beta[96] - 0.00391089865345172 beta[104]
   - 0.01839875509925 beta[192] + 0.00790875204305425 beta[200]
   + 0.00437351911007879 beta[288] - 0.00219178370344996 beta[289]
   - 0.0689047937516384 beta[290] + weighted_residual[18]
   = -0.0510423016744403
 R45: - 0.0306069726748393 beta[0] - 0.1142897528577104 beta[8]
   - 0.0168131195840609 beta[96] - 0.00477392244817723 beta[104]
   - 0.0179547876082887 beta[192] + 0.00606745248159453 beta[200]
   + 0.0134760745568541 beta[288] - 0.00277728658388678 beta[289]
   - 0.0990824836752071 beta[290] + weighted_residual[19]
   = -0.0530100517393158
Bounds
 -25 <= beta[0] <= 25
 -25 <= beta[8] <= 25
 -25 <= beta[96] <= 25
 -25 <= beta[104] <= 25
 -25 <= beta[192] <= 25
 -25 <= beta[200] <= 25
 beta[288] <= 1
 1e-08 <= beta[289] <= 0.9999999899999999
 1e-08 <= beta[290] <= 0.9999999899999999
 1e-08 <= beta[291] <= 0.9999999899999999
 weighted_residual[0] free
 weighted_residual[1] free
 weighted_residual[2] free
 weighted_residual[3] free
 weighted_residual[4] free
 weighted_residual[5] free
 weighted_residual[6] free
 weighted_residual[7] free
 weighted_residual[8] free
 weighted_residual[9] free
 weighted_residual[10] free
 weighted_residual[11] free
 weighted_residual[12] free
 weighted_residual[13] free
 weighted_residual[14] free
 weighted_residual[15] free
 weighted_residual[16] free
 weighted_residual[17] free
 weighted_residual[18] free
 weighted_residual[19] free
Binaries
 selected[0] selected[8] selected[96] selected[104] selected[192]
 selected[200] selected[288] selected[289] selected[290] selected[291]
End
