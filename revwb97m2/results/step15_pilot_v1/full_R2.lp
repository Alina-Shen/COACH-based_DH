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
 R2: beta[1] - 25 selected[1] <= 0
 R3: beta[1] + 25 selected[1] >= 0
 R4: beta[2] - 25 selected[2] <= 0
 R5: beta[2] + 25 selected[2] >= 0
 R6: beta[3] - 25 selected[3] <= 0
 R7: beta[3] + 25 selected[3] >= 0
 R8: beta[4] - 25 selected[4] <= 0
 R9: beta[4] + 25 selected[4] >= 0
 R10: beta[5] - 25 selected[5] <= 0
 R11: beta[5] + 25 selected[5] >= 0
 R12: beta[6] - 25 selected[6] <= 0
 R13: beta[6] + 25 selected[6] >= 0
 R14: beta[7] - 25 selected[7] <= 0
 R15: beta[7] + 25 selected[7] >= 0
 R16: beta[8] - 25 selected[8] <= 0
 R17: beta[8] + 25 selected[8] >= 0
 R18: beta[9] - 25 selected[9] <= 0
 R19: beta[9] + 25 selected[9] >= 0
 R20: beta[10] - 25 selected[10] <= 0
 R21: beta[10] + 25 selected[10] >= 0
 R22: beta[11] - 25 selected[11] <= 0
 R23: beta[11] + 25 selected[11] >= 0
 R24: beta[12] - 25 selected[12] <= 0
 R25: beta[12] + 25 selected[12] >= 0
 R26: beta[13] - 25 selected[13] <= 0
 R27: beta[13] + 25 selected[13] >= 0
 R28: beta[14] - 25 selected[14] <= 0
 R29: beta[14] + 25 selected[14] >= 0
 R30: beta[15] - 25 selected[15] <= 0
 R31: beta[15] + 25 selected[15] >= 0
 R32: beta[16] - 25 selected[16] <= 0
 R33: beta[16] + 25 selected[16] >= 0
 R34: beta[17] - 25 selected[17] <= 0
 R35: beta[17] + 25 selected[17] >= 0
 R36: beta[18] - 25 selected[18] <= 0
 R37: beta[18] + 25 selected[18] >= 0
 R38: beta[19] - 25 selected[19] <= 0
 R39: beta[19] + 25 selected[19] >= 0
 R40: beta[20] - 25 selected[20] <= 0
 R41: beta[20] + 25 selected[20] >= 0
 R42: beta[21] - 25 selected[21] <= 0
 R43: beta[21] + 25 selected[21] >= 0
 R44: beta[22] - 25 selected[22] <= 0
 R45: beta[22] + 25 selected[22] >= 0
 R46: beta[23] - 25 selected[23] <= 0
 R47: beta[23] + 25 selected[23] >= 0
 R48: beta[24] - 25 selected[24] <= 0
 R49: beta[24] + 25 selected[24] >= 0
 R50: beta[25] - 25 selected[25] <= 0
 R51: beta[25] + 25 selected[25] >= 0
 R52: beta[26] - 25 selected[26] <= 0
 R53: beta[26] + 25 selected[26] >= 0
 R54: beta[27] - 25 selected[27] <= 0
 R55: beta[27] + 25 selected[27] >= 0
 R56: beta[28] - 25 selected[28] <= 0
 R57: beta[28] + 25 selected[28] >= 0
 R58: beta[29] - 25 selected[29] <= 0
 R59: beta[29] + 25 selected[29] >= 0
 R60: beta[30] - 25 selected[30] <= 0
 R61: beta[30] + 25 selected[30] >= 0
 R62: beta[31] - 25 selected[31] <= 0
 R63: beta[31] + 25 selected[31] >= 0
 R64: beta[32] - 25 selected[32] <= 0
 R65: beta[32] + 25 selected[32] >= 0
 R66: beta[33] - 25 selected[33] <= 0
 R67: beta[33] + 25 selected[33] >= 0
 R68: beta[34] - 25 selected[34] <= 0
 R69: beta[34] + 25 selected[34] >= 0
 R70: beta[35] - 25 selected[35] <= 0
 R71: beta[35] + 25 selected[35] >= 0
 R72: beta[36] - 25 selected[36] <= 0
 R73: beta[36] + 25 selected[36] >= 0
 R74: beta[37] - 25 selected[37] <= 0
 R75: beta[37] + 25 selected[37] >= 0
 R76: beta[38] - 25 selected[38] <= 0
 R77: beta[38] + 25 selected[38] >= 0
 R78: beta[39] - 25 selected[39] <= 0
 R79: beta[39] + 25 selected[39] >= 0
 R80: beta[40] - 25 selected[40] <= 0
 R81: beta[40] + 25 selected[40] >= 0
 R82: beta[41] - 25 selected[41] <= 0
 R83: beta[41] + 25 selected[41] >= 0
 R84: beta[42] - 25 selected[42] <= 0
 R85: beta[42] + 25 selected[42] >= 0
 R86: beta[43] - 25 selected[43] <= 0
 R87: beta[43] + 25 selected[43] >= 0
 R88: beta[44] - 25 selected[44] <= 0
 R89: beta[44] + 25 selected[44] >= 0
 R90: beta[45] - 25 selected[45] <= 0
 R91: beta[45] + 25 selected[45] >= 0
 R92: beta[46] - 25 selected[46] <= 0
 R93: beta[46] + 25 selected[46] >= 0
 R94: beta[47] - 25 selected[47] <= 0
 R95: beta[47] + 25 selected[47] >= 0
 R96: beta[48] - 25 selected[48] <= 0
 R97: beta[48] + 25 selected[48] >= 0
 R98: beta[49] - 25 selected[49] <= 0
 R99: beta[49] + 25 selected[49] >= 0
 R100: beta[50] - 25 selected[50] <= 0
 R101: beta[50] + 25 selected[50] >= 0
 R102: beta[51] - 25 selected[51] <= 0
 R103: beta[51] + 25 selected[51] >= 0
 R104: beta[52] - 25 selected[52] <= 0
 R105: beta[52] + 25 selected[52] >= 0
 R106: beta[53] - 25 selected[53] <= 0
 R107: beta[53] + 25 selected[53] >= 0
 R108: beta[54] - 25 selected[54] <= 0
 R109: beta[54] + 25 selected[54] >= 0
 R110: beta[55] - 25 selected[55] <= 0
 R111: beta[55] + 25 selected[55] >= 0
 R112: beta[56] - 25 selected[56] <= 0
 R113: beta[56] + 25 selected[56] >= 0
 R114: beta[57] - 25 selected[57] <= 0
 R115: beta[57] + 25 selected[57] >= 0
 R116: beta[58] - 25 selected[58] <= 0
 R117: beta[58] + 25 selected[58] >= 0
 R118: beta[59] - 25 selected[59] <= 0
 R119: beta[59] + 25 selected[59] >= 0
 R120: beta[60] - 25 selected[60] <= 0
 R121: beta[60] + 25 selected[60] >= 0
 R122: beta[61] - 25 selected[61] <= 0
 R123: beta[61] + 25 selected[61] >= 0
 R124: beta[62] - 25 selected[62] <= 0
 R125: beta[62] + 25 selected[62] >= 0
 R126: beta[63] - 25 selected[63] <= 0
 R127: beta[63] + 25 selected[63] >= 0
 R128: beta[64] - 25 selected[64] <= 0
 R129: beta[64] + 25 selected[64] >= 0
 R130: beta[65] - 25 selected[65] <= 0
 R131: beta[65] + 25 selected[65] >= 0
 R132: beta[66] - 25 selected[66] <= 0
 R133: beta[66] + 25 selected[66] >= 0
 R134: beta[67] - 25 selected[67] <= 0
 R135: beta[67] + 25 selected[67] >= 0
 R136: beta[68] - 25 selected[68] <= 0
 R137: beta[68] + 25 selected[68] >= 0
 R138: beta[69] - 25 selected[69] <= 0
 R139: beta[69] + 25 selected[69] >= 0
 R140: beta[70] - 25 selected[70] <= 0
 R141: beta[70] + 25 selected[70] >= 0
 R142: beta[71] - 25 selected[71] <= 0
 R143: beta[71] + 25 selected[71] >= 0
 R144: beta[72] - 25 selected[72] <= 0
 R145: beta[72] + 25 selected[72] >= 0
 R146: beta[73] - 25 selected[73] <= 0
 R147: beta[73] + 25 selected[73] >= 0
 R148: beta[74] - 25 selected[74] <= 0
 R149: beta[74] + 25 selected[74] >= 0
 R150: beta[75] - 25 selected[75] <= 0
 R151: beta[75] + 25 selected[75] >= 0
 R152: beta[76] - 25 selected[76] <= 0
 R153: beta[76] + 25 selected[76] >= 0
 R154: beta[77] - 25 selected[77] <= 0
 R155: beta[77] + 25 selected[77] >= 0
 R156: beta[78] - 25 selected[78] <= 0
 R157: beta[78] + 25 selected[78] >= 0
 R158: beta[79] - 25 selected[79] <= 0
 R159: beta[79] + 25 selected[79] >= 0
 R160: beta[80] - 25 selected[80] <= 0
 R161: beta[80] + 25 selected[80] >= 0
 R162: beta[81] - 25 selected[81] <= 0
 R163: beta[81] + 25 selected[81] >= 0
 R164: beta[82] - 25 selected[82] <= 0
 R165: beta[82] + 25 selected[82] >= 0
 R166: beta[83] - 25 selected[83] <= 0
 R167: beta[83] + 25 selected[83] >= 0
 R168: beta[84] - 25 selected[84] <= 0
 R169: beta[84] + 25 selected[84] >= 0
 R170: beta[85] - 25 selected[85] <= 0
 R171: beta[85] + 25 selected[85] >= 0
 R172: beta[86] - 25 selected[86] <= 0
 R173: beta[86] + 25 selected[86] >= 0
 R174: beta[87] - 25 selected[87] <= 0
 R175: beta[87] + 25 selected[87] >= 0
 R176: beta[88] - 25 selected[88] <= 0
 R177: beta[88] + 25 selected[88] >= 0
 R178: beta[89] - 25 selected[89] <= 0
 R179: beta[89] + 25 selected[89] >= 0
 R180: beta[90] - 25 selected[90] <= 0
 R181: beta[90] + 25 selected[90] >= 0
 R182: beta[91] - 25 selected[91] <= 0
 R183: beta[91] + 25 selected[91] >= 0
 R184: beta[92] - 25 selected[92] <= 0
 R185: beta[92] + 25 selected[92] >= 0
 R186: beta[93] - 25 selected[93] <= 0
 R187: beta[93] + 25 selected[93] >= 0
 R188: beta[94] - 25 selected[94] <= 0
 R189: beta[94] + 25 selected[94] >= 0
 R190: beta[95] - 25 selected[95] <= 0
 R191: beta[95] + 25 selected[95] >= 0
 R192: beta[96] - 25 selected[96] <= 0
 R193: beta[96] + 25 selected[96] >= 0
 R194: beta[97] - 25 selected[97] <= 0
 R195: beta[97] + 25 selected[97] >= 0
 R196: beta[98] - 25 selected[98] <= 0
 R197: beta[98] + 25 selected[98] >= 0
 R198: beta[99] - 25 selected[99] <= 0
 R199: beta[99] + 25 selected[99] >= 0
 R200: beta[100] - 25 selected[100] <= 0
 R201: beta[100] + 25 selected[100] >= 0
 R202: beta[101] - 25 selected[101] <= 0
 R203: beta[101] + 25 selected[101] >= 0
 R204: beta[102] - 25 selected[102] <= 0
 R205: beta[102] + 25 selected[102] >= 0
 R206: beta[103] - 25 selected[103] <= 0
 R207: beta[103] + 25 selected[103] >= 0
 R208: beta[104] - 25 selected[104] <= 0
 R209: beta[104] + 25 selected[104] >= 0
 R210: beta[105] - 25 selected[105] <= 0
 R211: beta[105] + 25 selected[105] >= 0
 R212: beta[106] - 25 selected[106] <= 0
 R213: beta[106] + 25 selected[106] >= 0
 R214: beta[107] - 25 selected[107] <= 0
 R215: beta[107] + 25 selected[107] >= 0
 R216: beta[108] - 25 selected[108] <= 0
 R217: beta[108] + 25 selected[108] >= 0
 R218: beta[109] - 25 selected[109] <= 0
 R219: beta[109] + 25 selected[109] >= 0
 R220: beta[110] - 25 selected[110] <= 0
 R221: beta[110] + 25 selected[110] >= 0
 R222: beta[111] - 25 selected[111] <= 0
 R223: beta[111] + 25 selected[111] >= 0
 R224: beta[112] - 25 selected[112] <= 0
 R225: beta[112] + 25 selected[112] >= 0
 R226: beta[113] - 25 selected[113] <= 0
 R227: beta[113] + 25 selected[113] >= 0
 R228: beta[114] - 25 selected[114] <= 0
 R229: beta[114] + 25 selected[114] >= 0
 R230: beta[115] - 25 selected[115] <= 0
 R231: beta[115] + 25 selected[115] >= 0
 R232: beta[116] - 25 selected[116] <= 0
 R233: beta[116] + 25 selected[116] >= 0
 R234: beta[117] - 25 selected[117] <= 0
 R235: beta[117] + 25 selected[117] >= 0
 R236: beta[118] - 25 selected[118] <= 0
 R237: beta[118] + 25 selected[118] >= 0
 R238: beta[119] - 25 selected[119] <= 0
 R239: beta[119] + 25 selected[119] >= 0
 R240: beta[120] - 25 selected[120] <= 0
 R241: beta[120] + 25 selected[120] >= 0
 R242: beta[121] - 25 selected[121] <= 0
 R243: beta[121] + 25 selected[121] >= 0
 R244: beta[122] - 25 selected[122] <= 0
 R245: beta[122] + 25 selected[122] >= 0
 R246: beta[123] - 25 selected[123] <= 0
 R247: beta[123] + 25 selected[123] >= 0
 R248: beta[124] - 25 selected[124] <= 0
 R249: beta[124] + 25 selected[124] >= 0
 R250: beta[125] - 25 selected[125] <= 0
 R251: beta[125] + 25 selected[125] >= 0
 R252: beta[126] - 25 selected[126] <= 0
 R253: beta[126] + 25 selected[126] >= 0
 R254: beta[127] - 25 selected[127] <= 0
 R255: beta[127] + 25 selected[127] >= 0
 R256: beta[128] - 25 selected[128] <= 0
 R257: beta[128] + 25 selected[128] >= 0
 R258: beta[129] - 25 selected[129] <= 0
 R259: beta[129] + 25 selected[129] >= 0
 R260: beta[130] - 25 selected[130] <= 0
 R261: beta[130] + 25 selected[130] >= 0
 R262: beta[131] - 25 selected[131] <= 0
 R263: beta[131] + 25 selected[131] >= 0
 R264: beta[132] - 25 selected[132] <= 0
 R265: beta[132] + 25 selected[132] >= 0
 R266: beta[133] - 25 selected[133] <= 0
 R267: beta[133] + 25 selected[133] >= 0
 R268: beta[134] - 25 selected[134] <= 0
 R269: beta[134] + 25 selected[134] >= 0
 R270: beta[135] - 25 selected[135] <= 0
 R271: beta[135] + 25 selected[135] >= 0
 R272: beta[136] - 25 selected[136] <= 0
 R273: beta[136] + 25 selected[136] >= 0
 R274: beta[137] - 25 selected[137] <= 0
 R275: beta[137] + 25 selected[137] >= 0
 R276: beta[138] - 25 selected[138] <= 0
 R277: beta[138] + 25 selected[138] >= 0
 R278: beta[139] - 25 selected[139] <= 0
 R279: beta[139] + 25 selected[139] >= 0
 R280: beta[140] - 25 selected[140] <= 0
 R281: beta[140] + 25 selected[140] >= 0
 R282: beta[141] - 25 selected[141] <= 0
 R283: beta[141] + 25 selected[141] >= 0
 R284: beta[142] - 25 selected[142] <= 0
 R285: beta[142] + 25 selected[142] >= 0
 R286: beta[143] - 25 selected[143] <= 0
 R287: beta[143] + 25 selected[143] >= 0
 R288: beta[144] - 25 selected[144] <= 0
 R289: beta[144] + 25 selected[144] >= 0
 R290: beta[145] - 25 selected[145] <= 0
 R291: beta[145] + 25 selected[145] >= 0
 R292: beta[146] - 25 selected[146] <= 0
 R293: beta[146] + 25 selected[146] >= 0
 R294: beta[147] - 25 selected[147] <= 0
 R295: beta[147] + 25 selected[147] >= 0
 R296: beta[148] - 25 selected[148] <= 0
 R297: beta[148] + 25 selected[148] >= 0
 R298: beta[149] - 25 selected[149] <= 0
 R299: beta[149] + 25 selected[149] >= 0
 R300: beta[150] - 25 selected[150] <= 0
 R301: beta[150] + 25 selected[150] >= 0
 R302: beta[151] - 25 selected[151] <= 0
 R303: beta[151] + 25 selected[151] >= 0
 R304: beta[152] - 25 selected[152] <= 0
 R305: beta[152] + 25 selected[152] >= 0
 R306: beta[153] - 25 selected[153] <= 0
 R307: beta[153] + 25 selected[153] >= 0
 R308: beta[154] - 25 selected[154] <= 0
 R309: beta[154] + 25 selected[154] >= 0
 R310: beta[155] - 25 selected[155] <= 0
 R311: beta[155] + 25 selected[155] >= 0
 R312: beta[156] - 25 selected[156] <= 0
 R313: beta[156] + 25 selected[156] >= 0
 R314: beta[157] - 25 selected[157] <= 0
 R315: beta[157] + 25 selected[157] >= 0
 R316: beta[158] - 25 selected[158] <= 0
 R317: beta[158] + 25 selected[158] >= 0
 R318: beta[159] - 25 selected[159] <= 0
 R319: beta[159] + 25 selected[159] >= 0
 R320: beta[160] - 25 selected[160] <= 0
 R321: beta[160] + 25 selected[160] >= 0
 R322: beta[161] - 25 selected[161] <= 0
 R323: beta[161] + 25 selected[161] >= 0
 R324: beta[162] - 25 selected[162] <= 0
 R325: beta[162] + 25 selected[162] >= 0
 R326: beta[163] - 25 selected[163] <= 0
 R327: beta[163] + 25 selected[163] >= 0
 R328: beta[164] - 25 selected[164] <= 0
 R329: beta[164] + 25 selected[164] >= 0
 R330: beta[165] - 25 selected[165] <= 0
 R331: beta[165] + 25 selected[165] >= 0
 R332: beta[166] - 25 selected[166] <= 0
 R333: beta[166] + 25 selected[166] >= 0
 R334: beta[167] - 25 selected[167] <= 0
 R335: beta[167] + 25 selected[167] >= 0
 R336: beta[168] - 25 selected[168] <= 0
 R337: beta[168] + 25 selected[168] >= 0
 R338: beta[169] - 25 selected[169] <= 0
 R339: beta[169] + 25 selected[169] >= 0
 R340: beta[170] - 25 selected[170] <= 0
 R341: beta[170] + 25 selected[170] >= 0
 R342: beta[171] - 25 selected[171] <= 0
 R343: beta[171] + 25 selected[171] >= 0
 R344: beta[172] - 25 selected[172] <= 0
 R345: beta[172] + 25 selected[172] >= 0
 R346: beta[173] - 25 selected[173] <= 0
 R347: beta[173] + 25 selected[173] >= 0
 R348: beta[174] - 25 selected[174] <= 0
 R349: beta[174] + 25 selected[174] >= 0
 R350: beta[175] - 25 selected[175] <= 0
 R351: beta[175] + 25 selected[175] >= 0
 R352: beta[176] - 25 selected[176] <= 0
 R353: beta[176] + 25 selected[176] >= 0
 R354: beta[177] - 25 selected[177] <= 0
 R355: beta[177] + 25 selected[177] >= 0
 R356: beta[178] - 25 selected[178] <= 0
 R357: beta[178] + 25 selected[178] >= 0
 R358: beta[179] - 25 selected[179] <= 0
 R359: beta[179] + 25 selected[179] >= 0
 R360: beta[180] - 25 selected[180] <= 0
 R361: beta[180] + 25 selected[180] >= 0
 R362: beta[181] - 25 selected[181] <= 0
 R363: beta[181] + 25 selected[181] >= 0
 R364: beta[182] - 25 selected[182] <= 0
 R365: beta[182] + 25 selected[182] >= 0
 R366: beta[183] - 25 selected[183] <= 0
 R367: beta[183] + 25 selected[183] >= 0
 R368: beta[184] - 25 selected[184] <= 0
 R369: beta[184] + 25 selected[184] >= 0
 R370: beta[185] - 25 selected[185] <= 0
 R371: beta[185] + 25 selected[185] >= 0
 R372: beta[186] - 25 selected[186] <= 0
 R373: beta[186] + 25 selected[186] >= 0
 R374: beta[187] - 25 selected[187] <= 0
 R375: beta[187] + 25 selected[187] >= 0
 R376: beta[188] - 25 selected[188] <= 0
 R377: beta[188] + 25 selected[188] >= 0
 R378: beta[189] - 25 selected[189] <= 0
 R379: beta[189] + 25 selected[189] >= 0
 R380: beta[190] - 25 selected[190] <= 0
 R381: beta[190] + 25 selected[190] >= 0
 R382: beta[191] - 25 selected[191] <= 0
 R383: beta[191] + 25 selected[191] >= 0
 R384: beta[192] - 25 selected[192] <= 0
 R385: beta[192] + 25 selected[192] >= 0
 R386: beta[193] - 25 selected[193] <= 0
 R387: beta[193] + 25 selected[193] >= 0
 R388: beta[194] - 25 selected[194] <= 0
 R389: beta[194] + 25 selected[194] >= 0
 R390: beta[195] - 25 selected[195] <= 0
 R391: beta[195] + 25 selected[195] >= 0
 R392: beta[196] - 25 selected[196] <= 0
 R393: beta[196] + 25 selected[196] >= 0
 R394: beta[197] - 25 selected[197] <= 0
 R395: beta[197] + 25 selected[197] >= 0
 R396: beta[198] - 25 selected[198] <= 0
 R397: beta[198] + 25 selected[198] >= 0
 R398: beta[199] - 25 selected[199] <= 0
 R399: beta[199] + 25 selected[199] >= 0
 R400: beta[200] - 25 selected[200] <= 0
 R401: beta[200] + 25 selected[200] >= 0
 R402: beta[201] - 25 selected[201] <= 0
 R403: beta[201] + 25 selected[201] >= 0
 R404: beta[202] - 25 selected[202] <= 0
 R405: beta[202] + 25 selected[202] >= 0
 R406: beta[203] - 25 selected[203] <= 0
 R407: beta[203] + 25 selected[203] >= 0
 R408: beta[204] - 25 selected[204] <= 0
 R409: beta[204] + 25 selected[204] >= 0
 R410: beta[205] - 25 selected[205] <= 0
 R411: beta[205] + 25 selected[205] >= 0
 R412: beta[206] - 25 selected[206] <= 0
 R413: beta[206] + 25 selected[206] >= 0
 R414: beta[207] - 25 selected[207] <= 0
 R415: beta[207] + 25 selected[207] >= 0
 R416: beta[208] - 25 selected[208] <= 0
 R417: beta[208] + 25 selected[208] >= 0
 R418: beta[209] - 25 selected[209] <= 0
 R419: beta[209] + 25 selected[209] >= 0
 R420: beta[210] - 25 selected[210] <= 0
 R421: beta[210] + 25 selected[210] >= 0
 R422: beta[211] - 25 selected[211] <= 0
 R423: beta[211] + 25 selected[211] >= 0
 R424: beta[212] - 25 selected[212] <= 0
 R425: beta[212] + 25 selected[212] >= 0
 R426: beta[213] - 25 selected[213] <= 0
 R427: beta[213] + 25 selected[213] >= 0
 R428: beta[214] - 25 selected[214] <= 0
 R429: beta[214] + 25 selected[214] >= 0
 R430: beta[215] - 25 selected[215] <= 0
 R431: beta[215] + 25 selected[215] >= 0
 R432: beta[216] - 25 selected[216] <= 0
 R433: beta[216] + 25 selected[216] >= 0
 R434: beta[217] - 25 selected[217] <= 0
 R435: beta[217] + 25 selected[217] >= 0
 R436: beta[218] - 25 selected[218] <= 0
 R437: beta[218] + 25 selected[218] >= 0
 R438: beta[219] - 25 selected[219] <= 0
 R439: beta[219] + 25 selected[219] >= 0
 R440: beta[220] - 25 selected[220] <= 0
 R441: beta[220] + 25 selected[220] >= 0
 R442: beta[221] - 25 selected[221] <= 0
 R443: beta[221] + 25 selected[221] >= 0
 R444: beta[222] - 25 selected[222] <= 0
 R445: beta[222] + 25 selected[222] >= 0
 R446: beta[223] - 25 selected[223] <= 0
 R447: beta[223] + 25 selected[223] >= 0
 R448: beta[224] - 25 selected[224] <= 0
 R449: beta[224] + 25 selected[224] >= 0
 R450: beta[225] - 25 selected[225] <= 0
 R451: beta[225] + 25 selected[225] >= 0
 R452: beta[226] - 25 selected[226] <= 0
 R453: beta[226] + 25 selected[226] >= 0
 R454: beta[227] - 25 selected[227] <= 0
 R455: beta[227] + 25 selected[227] >= 0
 R456: beta[228] - 25 selected[228] <= 0
 R457: beta[228] + 25 selected[228] >= 0
 R458: beta[229] - 25 selected[229] <= 0
 R459: beta[229] + 25 selected[229] >= 0
 R460: beta[230] - 25 selected[230] <= 0
 R461: beta[230] + 25 selected[230] >= 0
 R462: beta[231] - 25 selected[231] <= 0
 R463: beta[231] + 25 selected[231] >= 0
 R464: beta[232] - 25 selected[232] <= 0
 R465: beta[232] + 25 selected[232] >= 0
 R466: beta[233] - 25 selected[233] <= 0
 R467: beta[233] + 25 selected[233] >= 0
 R468: beta[234] - 25 selected[234] <= 0
 R469: beta[234] + 25 selected[234] >= 0
 R470: beta[235] - 25 selected[235] <= 0
 R471: beta[235] + 25 selected[235] >= 0
 R472: beta[236] - 25 selected[236] <= 0
 R473: beta[236] + 25 selected[236] >= 0
 R474: beta[237] - 25 selected[237] <= 0
 R475: beta[237] + 25 selected[237] >= 0
 R476: beta[238] - 25 selected[238] <= 0
 R477: beta[238] + 25 selected[238] >= 0
 R478: beta[239] - 25 selected[239] <= 0
 R479: beta[239] + 25 selected[239] >= 0
 R480: beta[240] - 25 selected[240] <= 0
 R481: beta[240] + 25 selected[240] >= 0
 R482: beta[241] - 25 selected[241] <= 0
 R483: beta[241] + 25 selected[241] >= 0
 R484: beta[242] - 25 selected[242] <= 0
 R485: beta[242] + 25 selected[242] >= 0
 R486: beta[243] - 25 selected[243] <= 0
 R487: beta[243] + 25 selected[243] >= 0
 R488: beta[244] - 25 selected[244] <= 0
 R489: beta[244] + 25 selected[244] >= 0
 R490: beta[245] - 25 selected[245] <= 0
 R491: beta[245] + 25 selected[245] >= 0
 R492: beta[246] - 25 selected[246] <= 0
 R493: beta[246] + 25 selected[246] >= 0
 R494: beta[247] - 25 selected[247] <= 0
 R495: beta[247] + 25 selected[247] >= 0
 R496: beta[248] - 25 selected[248] <= 0
 R497: beta[248] + 25 selected[248] >= 0
 R498: beta[249] - 25 selected[249] <= 0
 R499: beta[249] + 25 selected[249] >= 0
 R500: beta[250] - 25 selected[250] <= 0
 R501: beta[250] + 25 selected[250] >= 0
 R502: beta[251] - 25 selected[251] <= 0
 R503: beta[251] + 25 selected[251] >= 0
 R504: beta[252] - 25 selected[252] <= 0
 R505: beta[252] + 25 selected[252] >= 0
 R506: beta[253] - 25 selected[253] <= 0
 R507: beta[253] + 25 selected[253] >= 0
 R508: beta[254] - 25 selected[254] <= 0
 R509: beta[254] + 25 selected[254] >= 0
 R510: beta[255] - 25 selected[255] <= 0
 R511: beta[255] + 25 selected[255] >= 0
 R512: beta[256] - 25 selected[256] <= 0
 R513: beta[256] + 25 selected[256] >= 0
 R514: beta[257] - 25 selected[257] <= 0
 R515: beta[257] + 25 selected[257] >= 0
 R516: beta[258] - 25 selected[258] <= 0
 R517: beta[258] + 25 selected[258] >= 0
 R518: beta[259] - 25 selected[259] <= 0
 R519: beta[259] + 25 selected[259] >= 0
 R520: beta[260] - 25 selected[260] <= 0
 R521: beta[260] + 25 selected[260] >= 0
 R522: beta[261] - 25 selected[261] <= 0
 R523: beta[261] + 25 selected[261] >= 0
 R524: beta[262] - 25 selected[262] <= 0
 R525: beta[262] + 25 selected[262] >= 0
 R526: beta[263] - 25 selected[263] <= 0
 R527: beta[263] + 25 selected[263] >= 0
 R528: beta[264] - 25 selected[264] <= 0
 R529: beta[264] + 25 selected[264] >= 0
 R530: beta[265] - 25 selected[265] <= 0
 R531: beta[265] + 25 selected[265] >= 0
 R532: beta[266] - 25 selected[266] <= 0
 R533: beta[266] + 25 selected[266] >= 0
 R534: beta[267] - 25 selected[267] <= 0
 R535: beta[267] + 25 selected[267] >= 0
 R536: beta[268] - 25 selected[268] <= 0
 R537: beta[268] + 25 selected[268] >= 0
 R538: beta[269] - 25 selected[269] <= 0
 R539: beta[269] + 25 selected[269] >= 0
 R540: beta[270] - 25 selected[270] <= 0
 R541: beta[270] + 25 selected[270] >= 0
 R542: beta[271] - 25 selected[271] <= 0
 R543: beta[271] + 25 selected[271] >= 0
 R544: beta[272] - 25 selected[272] <= 0
 R545: beta[272] + 25 selected[272] >= 0
 R546: beta[273] - 25 selected[273] <= 0
 R547: beta[273] + 25 selected[273] >= 0
 R548: beta[274] - 25 selected[274] <= 0
 R549: beta[274] + 25 selected[274] >= 0
 R550: beta[275] - 25 selected[275] <= 0
 R551: beta[275] + 25 selected[275] >= 0
 R552: beta[276] - 25 selected[276] <= 0
 R553: beta[276] + 25 selected[276] >= 0
 R554: beta[277] - 25 selected[277] <= 0
 R555: beta[277] + 25 selected[277] >= 0
 R556: beta[278] - 25 selected[278] <= 0
 R557: beta[278] + 25 selected[278] >= 0
 R558: beta[279] - 25 selected[279] <= 0
 R559: beta[279] + 25 selected[279] >= 0
 R560: beta[280] - 25 selected[280] <= 0
 R561: beta[280] + 25 selected[280] >= 0
 R562: beta[281] - 25 selected[281] <= 0
 R563: beta[281] + 25 selected[281] >= 0
 R564: beta[282] - 25 selected[282] <= 0
 R565: beta[282] + 25 selected[282] >= 0
 R566: beta[283] - 25 selected[283] <= 0
 R567: beta[283] + 25 selected[283] >= 0
 R568: beta[284] - 25 selected[284] <= 0
 R569: beta[284] + 25 selected[284] >= 0
 R570: beta[285] - 25 selected[285] <= 0
 R571: beta[285] + 25 selected[285] >= 0
 R572: beta[286] - 25 selected[286] <= 0
 R573: beta[286] + 25 selected[286] >= 0
 R574: beta[287] - 25 selected[287] <= 0
 R575: beta[287] + 25 selected[287] >= 0
 R576: beta[288] - 25 selected[288] <= 0
 R577: beta[288] + 25 selected[288] >= 0
 R578: beta[289] - 25 selected[289] <= 0
 R579: beta[289] + 25 selected[289] >= 0
 R580: beta[290] - 25 selected[290] <= 0
 R581: beta[290] + 25 selected[290] >= 0
 R582: beta[291] - 25 selected[291] <= 0
 R583: beta[291] + 25 selected[291] >= 0
 R584: selected[288] = 1
 R585: selected[289] = 1
 R586: selected[290] = 1
 R587: selected[291] = 1
 support_budget: selected[0] + selected[1] + selected[2] + selected[3]
   + selected[4] + selected[5] + selected[6] + selected[7] + selected[8]
   + selected[9] + selected[10] + selected[11] + selected[12]
   + selected[13] + selected[14] + selected[15] + selected[16]
   + selected[17] + selected[18] + selected[19] + selected[20]
   + selected[21] + selected[22] + selected[23] + selected[24]
   + selected[25] + selected[26] + selected[27] + selected[28]
   + selected[29] + selected[30] + selected[31] + selected[32]
   + selected[33] + selected[34] + selected[35] + selected[36]
   + selected[37] + selected[38] + selected[39] + selected[40]
   + selected[41] + selected[42] + selected[43] + selected[44]
   + selected[45] + selected[46] + selected[47] + selected[48]
   + selected[49] + selected[50] + selected[51] + selected[52]
   + selected[53] + selected[54] + selected[55] + selected[56]
   + selected[57] + selected[58] + selected[59] + selected[60]
   + selected[61] + selected[62] + selected[63] + selected[64]
   + selected[65] + selected[66] + selected[67] + selected[68]
   + selected[69] + selected[70] + selected[71] + selected[72]
   + selected[73] + selected[74] + selected[75] + selected[76]
   + selected[77] + selected[78] + selected[79] + selected[80]
   + selected[81] + selected[82] + selected[83] + selected[84]
   + selected[85] + selected[86] + selected[87] + selected[88]
   + selected[89] + selected[90] + selected[91] + selected[92]
   + selected[93] + selected[94] + selected[95] + selected[96]
   + selected[97] + selected[98] + selected[99] + selected[100]
   + selected[101] + selected[102] + selected[103] + selected[104]
   + selected[105] + selected[106] + selected[107] + selected[108]
   + selected[109] + selected[110] + selected[111] + selected[112]
   + selected[113] + selected[114] + selected[115] + selected[116]
   + selected[117] + selected[118] + selected[119] + selected[120]
   + selected[121] + selected[122] + selected[123] + selected[124]
   + selected[125] + selected[126] + selected[127] + selected[128]
   + selected[129] + selected[130] + selected[131] + selected[132]
   + selected[133] + selected[134] + selected[135] + selected[136]
   + selected[137] + selected[138] + selected[139] + selected[140]
   + selected[141] + selected[142] + selected[143] + selected[144]
   + selected[145] + selected[146] + selected[147] + selected[148]
   + selected[149] + selected[150] + selected[151] + selected[152]
   + selected[153] + selected[154] + selected[155] + selected[156]
   + selected[157] + selected[158] + selected[159] + selected[160]
   + selected[161] + selected[162] + selected[163] + selected[164]
   + selected[165] + selected[166] + selected[167] + selected[168]
   + selected[169] + selected[170] + selected[171] + selected[172]
   + selected[173] + selected[174] + selected[175] + selected[176]
   + selected[177] + selected[178] + selected[179] + selected[180]
   + selected[181] + selected[182] + selected[183] + selected[184]
   + selected[185] + selected[186] + selected[187] + selected[188]
   + selected[189] + selected[190] + selected[191] + selected[192]
   + selected[193] + selected[194] + selected[195] + selected[196]
   + selected[197] + selected[198] + selected[199] + selected[200]
   + selected[201] + selected[202] + selected[203] + selected[204]
   + selected[205] + selected[206] + selected[207] + selected[208]
   + selected[209] + selected[210] + selected[211] + selected[212]
   + selected[213] + selected[214] + selected[215] + selected[216]
   + selected[217] + selected[218] + selected[219] + selected[220]
   + selected[221] + selected[222] + selected[223] + selected[224]
   + selected[225] + selected[226] + selected[227] + selected[228]
   + selected[229] + selected[230] + selected[231] + selected[232]
   + selected[233] + selected[234] + selected[235] + selected[236]
   + selected[237] + selected[238] + selected[239] + selected[240]
   + selected[241] + selected[242] + selected[243] + selected[244]
   + selected[245] + selected[246] + selected[247] + selected[248]
   + selected[249] + selected[250] + selected[251] + selected[252]
   + selected[253] + selected[254] + selected[255] + selected[256]
   + selected[257] + selected[258] + selected[259] + selected[260]
   + selected[261] + selected[262] + selected[263] + selected[264]
   + selected[265] + selected[266] + selected[267] + selected[268]
   + selected[269] + selected[270] + selected[271] + selected[272]
   + selected[273] + selected[274] + selected[275] + selected[276]
   + selected[277] + selected[278] + selected[279] + selected[280]
   + selected[281] + selected[282] + selected[283] + selected[284]
   + selected[285] + selected[286] + selected[287] + selected[288]
   + selected[289] + selected[290] + selected[291] <= 14
 UEG_exchange: beta[0] - 0.5 beta[16] + 0.375 beta[32] - 0.3125 beta[48]
   + 0.2734375 beta[64] - 0.24609375 beta[80] + beta[288] = 1
 R590: - 0.2522016449708661 beta[0] - 0.0155853769718576 beta[1]
   + 0.00406400943990683 beta[2] + 0.00305476031777199 beta[3]
   + 0.00123717480295198 beta[4] + 3.6007846028232891e-04 beta[5]
   + 3.61633e-05 beta[6] - 5.871e-05 beta[7] + 0.1838898055741412 beta[8]
   - 0.00171320471192724 beta[9] - 0.00475209 beta[10]
   - 0.00202608376591404 beta[11] - 6.3014939056024873e-04 beta[12]
   - 1.1558553089960588e-04 beta[13] + 3.97479e-05 beta[14]
   + 7.08431e-05 beta[15] - 0.0708889380018726 beta[16]
   + 0.0277034250170452 beta[17] + 0.00723640169416135 beta[18]
   + 0.0014376666716172 beta[19] + 1.6316953092352336e-04 beta[20]
   - 6.50682e-05 beta[21] - 7.74903e-05 beta[22] - 5.71856e-05 beta[23]
   - 0.0788922763642631 beta[24] - 0.0457270406697437 beta[25]
   - 0.00934875639247356 beta[26] - 0.00160277301414148 beta[27]
   - 1.9020982240763171e-04 beta[28] + 1.02777e-05 beta[29]
   + 1.37947e-05 beta[30] + 9.02583e-07 beta[31]
   + 0.2652692465935985 beta[32] + 0.0465493565106658 beta[33]
   + 0.00791024900277478 beta[34] + 0.00140971449316671 beta[35]
   + 3.1037929935654249e-04 beta[36] + 0.000123323 beta[37]
   + 8.22147e-05 beta[38] + 6.29007e-05 beta[39]
   - 0.3098080119379959 beta[40] - 0.0276603813705324 beta[41]
   - 0.0027381620821896 beta[42] - 2.4454029353596974e-04 beta[43]
   - 1.0244652702252543e-04 beta[44] - 1.1601234934756456e-04 beta[45]
   - 0.000104804 beta[46] - 8.32454e-05 beta[47]
   + 0.0995959308907712 beta[48] - 0.00532280065116081 beta[49]
   - 0.00403197866981473 beta[50] - 0.00145988648359379 beta[51]
   - 4.0850389904083782e-04 beta[52] - 6.95774e-05 beta[53]
   + 2.3402e-05 beta[54] + 4.18903e-05 beta[55]
   - 0.0416038101113587 beta[56] + 0.0194860547477454 beta[57]
   + 0.00830487583349249 beta[58] + 0.00280920047993307 beta[59]
   + 9.2914710413805361e-04 beta[60] + 3.1732958525332094e-04 beta[61]
   + 1.1164013595653093e-04 beta[62] + 3.77471e-05 beta[63]
   + 0.4374950032615146 beta[64] + 0.0107035768702284 beta[65]
   - 0.0061547489956377 beta[66] - 0.00288582199211854 beta[67]
   - 0.00113391573256283 beta[68] - 0.000475452 beta[69]
   - 2.2108761897024625e-04 beta[70] - 0.000112115 beta[71]
   - 0.8125932876413977 beta[72] - 0.0550737222774047 beta[73]
   - 9.0429074366591409e-04 beta[74] + 0.00148176697952402 beta[75]
   + 8.4103447260341739e-04 beta[76] + 4.3642883696487348e-04 beta[77]
   + 2.4077059593112171e-04 beta[78] + 1.4163946593774262e-04 beta[79]
   + 0.7641039156518246 beta[80] + 0.0733118867587153 beta[81]
   + 0.00728172106655232 beta[82] + 5.317702627791012e-04 beta[83]
   - 0.00017448 beta[84] - 2.0014317399398213e-04 beta[85]
   - 1.5262451805381428e-04 beta[86] - 1.0896225272935867e-04 beta[87]
   - 0.5407307978795963 beta[88] - 0.0641679087516357 beta[89]
   - 0.00948029347775761 beta[90] - 0.00198478474026906 beta[91]
   - 0.000505547 beta[92] - 1.1662572033317003e-04 beta[93]
   - 2.97587e-06 beta[94] + 2.81412e-05 beta[95]
   + 0.0116581467647352 beta[96] - 3.0917466903287815e-04 beta[97]
   - 5.033633487445011e-04 beta[98] - 2.4103418516550963e-04 beta[99]
   - 1.2723078789949533e-04 beta[100] - 8.4029e-05 beta[101]
   - 6.61778e-05 beta[102] - 5.68887e-05 beta[103] + 4.20098e-05 beta[104]
   + 9.1976534882575193e-04 beta[105] + 5.0125819422594845e-04 beta[106]
   + 2.595133500837896e-04 beta[107] + 1.5112764445381088e-04 beta[108]
   + 0.000100337 beta[109] + 7.38671e-05 beta[110] + 5.82492e-05 beta[111]
   - 0.00726001899253459 beta[112] - 5.9385044519834427e-04 beta[113]
   - 1.3704438948312903e-04 beta[114] - 9.76599e-05 beta[115]
   - 7.74774e-05 beta[116] - 6.02086e-05 beta[117] - 4.66104e-05 beta[118]
   - 3.64763e-05 beta[119] + 0.00388075445055502 beta[120]
   - 6.7366652116648417e-04 beta[121] - 4.34020476861859e-04 beta[122]
   - 0.000196654 beta[123] - 8.95299e-05 beta[124] - 4.32602e-05 beta[125]
   - 2.26654e-05 beta[126] - 1.30273e-05 beta[127]
   + 0.00639535485938489 beta[128] + 0.00200453142445895 beta[129]
   + 7.9561521641353093e-04 beta[130] + 3.8536532287303206e-04 beta[131]
   + 2.1370448374472901e-04 beta[132] + 1.310098162785341e-04 beta[133]
   + 8.67203e-05 beta[134] + 6.09382e-05 beta[135]
   - 0.0108279607117306 beta[136] - 0.0018690793835201 beta[137]
   - 0.000641388 beta[138] - 3.2997488400389468e-04 beta[139]
   - 2.0411212001499737e-04 beta[140] - 1.3908245744432445e-04 beta[141]
   - 0.000100512 beta[142] - 7.55997e-05 beta[143]
   - 0.003879808802427 beta[144] - 0.00113227504265389 beta[145]
   - 0.000209406 beta[146] + 8.51587e-06 beta[147] + 5.54764e-05 beta[148]
   + 6.0521e-05 beta[149] + 5.52534e-05 beta[150] + 4.80101e-05 beta[151]
   + 0.0180136904456027 beta[152] + 0.00387257276560639 beta[153]
   + 0.00111800120160086 beta[154] + 3.9508852219021114e-04 beta[155]
   + 1.5722839915526592e-04 beta[156] + 6.57643e-05 beta[157]
   + 2.64075e-05 beta[158] + 8.0825e-06 beta[159]
   - 0.00534828294902017 beta[160] - 0.00222040024365434 beta[161]
   - 0.00104182273235239 beta[162] - 5.2270244152561045e-04 beta[163]
   - 2.8075149039600151e-04 beta[164] - 1.613071741945378e-04 beta[165]
   - 9.82838e-05 beta[166] - 6.27629e-05 beta[167]
   - 0.0127435173908196 beta[168] - 0.00126114149368102 beta[169]
   + 1.4639343122185505e-04 beta[170] + 2.6743732043532225e-04 beta[171]
   + 0.000215914 beta[172] + 1.5761919793130626e-04 beta[173]
   + 1.1407362289130633e-04 beta[174] + 8.37279e-05 beta[175]
   + 0.0101493080838306 beta[176] + 0.00245215509682117 beta[177]
   + 6.1215028606250376e-04 beta[178] + 1.155217981526847e-04 beta[179]
   - 2.56646e-05 beta[180] - 6.15159e-05 beta[181] - 6.49167e-05 beta[182]
   - 5.88289e-05 beta[183] - 9.300094912679317e-04 beta[184]
   - 0.00188223314928874 beta[185] - 8.3890917086633832e-04 beta[186]
   - 3.5482971419121347e-04 beta[187] - 1.472011156994302e-04 beta[188]
   - 5.53453e-05 beta[189] - 1.34645e-05 beta[190] + 5.77276e-06 beta[191]
   - 0.00311292910454243 beta[192] - 0.00214868732682559 beta[193]
   + 5.8324147715687117e-04 beta[194] + 0.00265583622035191 beta[195]
   + 6.8734433052926465e-04 beta[196] - 0.0028657953946189 beta[197]
   - 0.00195456156891613 beta[198] + 0.00277038249963882 beta[199]
   - 0.00845288273770085 beta[200] + 6.8337568393819531e-04 beta[201]
   + 0.00468720525701493 beta[202] - 0.000622392 beta[203]
   - 0.00379886801806109 beta[204] + 6.5870278930081649e-04 beta[205]
   + 0.00352038503795095 beta[206] - 7.6933670085016265e-04 beta[207]
   - 0.0145135928766824 beta[208] - 4.88128e-06 beta[209]
   + 0.00727265040797002 beta[210] - 0.000213775 beta[211]
   - 0.00592271199488139 beta[212] + 5.6777e-05 beta[213]
   + 0.0054994477108251 beta[214] + 5.0137379482894468e-04 beta[215]
   - 0.00215339766352972 beta[216] - 8.4798478005928667e-04 beta[217]
   + 8.9403147753490256e-04 beta[218] + 0.00140892321401671 beta[219]
   + 4.43925e-06 beta[220] - 0.00149181025088423 beta[221]
   - 8.5137743974217914e-04 beta[222] + 0.00107868054968204 beta[223]
   + 0.0189275315593083 beta[224] + 9.2276081192091452e-04 beta[225]
   - 0.00943963124580084 beta[226] - 0.00153745440155678 beta[227]
   + 0.00676857500312545 beta[228] + 0.00186878075695465 beta[229]
   - 0.00518408 beta[230] - 0.00192352180736081 beta[231]
   + 0.010127891735765 beta[232] + 8.2837253653160372e-04 beta[233]
   - 0.00476974816449405 beta[234] - 0.0010532338314362 beta[235]
   + 0.00322870603662798 beta[236] + 0.00107844045365147 beta[237]
   - 0.00236399634692305 beta[238] - 0.000935452 beta[239]
   - 0.0115019612460225 beta[240] - 0.00122516268889615 beta[241]
   + 0.00539409176938863 beta[242] + 0.00169974692133692 beta[243]
   - 0.00345338453186701 beta[244] - 0.00179132202714164 beta[245]
   + 0.0022162792459147 beta[246] + 0.00146917871536694 beta[247]
   - 0.00568659476608534 beta[248] - 3.18378e-05 beta[249]
   + 0.00293832442777121 beta[250] + 2.64641e-05 beta[251]
   - 0.00249088582305578 beta[252] - 1.8323181806653962e-04 beta[253]
   + 0.00247692583780009 beta[254] + 6.8545557742470133e-04 beta[255]
   + 0.0045759170116526 beta[256] + 0.000221563 beta[257]
   - 0.00214157831345368 beta[258] - 0.000136273 beta[259]
   + 0.00159553331592105 beta[260] + 3.01604e-05 beta[261]
   - 0.00152462160337906 beta[262] - 1.389365183211083e-04 beta[263]
   + 0.0037632994423082 beta[264] + 3.67714e-05 beta[265]
   - 0.0021725938976017 beta[266] - 3.5126531252842368e-04 beta[267]
   + 0.00185014448914675 beta[268] + 0.000797897 beta[269]
   - 0.0015129484917051 beta[270] - 0.00118161321420643 beta[271]
   - 0.00232610776595187 beta[272] + 7.7369486985534889e-04 beta[273]
   + 0.0015938938019443 beta[274] - 8.7326769934546061e-04 beta[275]
   - 0.00172055463301569 beta[276] + 6.6703024669068284e-04 beta[277]
   + 0.00184389674777518 beta[278] - 2.9426956973376483e-04 beta[279]
   - 0.00914458908854423 beta[280] - 0.00123137056701989 beta[281]
   + 0.00420306333837109 beta[282] + 0.00169152814942739 beta[283]
   - 0.00259519272022176 beta[284] - 0.00184633860050042 beta[285]
   + 0.00152448327368525 beta[286] + 0.00171420334043752 beta[287]
   - 0.2921209532227276 beta[288] + 5.3847042806377549e-04 beta[289]
   - 0.015956572064799 beta[290] - 4.9866e-09 beta[291]
   + weighted_residual[0] = -0.290127464393108
 R591: - 0.2216728194322263 beta[0] - 0.00590536273764357 beta[1]
   - 0.00240183545174705 beta[2] - 0.00152454084577911 beta[3]
   - 0.000779249 beta[4] - 3.5176833984654692e-04 beta[5]
   - 1.4503060118130831e-04 beta[6] - 5.3922e-05 beta[7]
   + 0.0914860448807573 beta[8] - 0.00434352395698363 beta[9]
   + 6.0975773279086927e-04 beta[10] + 6.901556990446733e-04 beta[11]
   + 0.000322764 beta[12] + 1.1257417884852965e-04 beta[13]
   + 2.23499e-05 beta[14] - 1.0371e-05 beta[15]
   + 0.0945544056945729 beta[16] + 0.0152444217543809 beta[17]
   + 0.00148437913298996 beta[18] + 3.373184565711796e-04 beta[19]
   + 2.4382047439615946e-04 beta[20] + 0.000189081 beta[21]
   + 1.3657019090531258e-04 beta[22] + 9.65638e-05 beta[23]
   - 0.2129271307323808 beta[24] - 0.0177542034773495 beta[25]
   - 0.0024766354088441 beta[26] - 9.4871061538620376e-04 beta[27]
   - 5.7652846464033172e-04 beta[28] - 3.6410956431319675e-04 beta[29]
   - 2.3024278885510751e-04 beta[30] - 1.4925828229831102e-04 beta[31]
   + 0.2525750061872278 beta[32] + 0.0146340440544729 beta[33]
   + 0.00220189972958719 beta[34] + 9.732718825125505e-04 beta[35]
   + 5.7613656798436623e-04 beta[36] + 3.4899574851249819e-04 beta[37]
   + 2.1602487429815871e-04 beta[38] + 1.393204341280006e-04 beta[39]
   - 0.3295059966535536 beta[40] - 0.0171576844605884 beta[41]
   - 0.00175738937167417 beta[42] - 0.00064642 beta[43]
   - 3.615186195531834e-04 beta[44] - 2.0900133029959318e-04 beta[45]
   - 1.2648845871670903e-04 beta[46] - 8.17914e-05 beta[47]
   + 0.4054611570809287 beta[48] + 0.0254970972926737 beta[49]
   + 0.00215657110697425 beta[50] + 0.000398088 beta[51]
   + 1.4295575065123979e-04 beta[52] + 6.16992e-05 beta[53]
   + 3.04756e-05 beta[54] + 1.81375e-05 beta[55]
   - 0.2863490512025934 beta[56] - 0.0252049063771887 beta[57]
   - 0.00284349424935628 beta[58] - 0.000461909 beta[59]
   - 7.82953e-05 beta[60] + 3.03996e-06 beta[61] + 1.77194e-05 beta[62]
   + 1.66357e-05 beta[63] + 0.0333989079168849 beta[64]
   + 0.0130266140756601 beta[65] + 0.0028033997879107 beta[66]
   + 0.00069846 beta[67] + 1.7109164958224653e-04 beta[68]
   + 3.03193e-05 beta[69] - 5.57238e-06 beta[70] - 1.29301e-05 beta[71]
   + 0.0639627979891747 beta[72] - 0.00381035284083926 beta[73]
   - 0.00237728030392703 beta[74] - 8.8438541380144299e-04 beta[75]
   - 3.0731044149002828e-04 beta[76] - 1.0925088234800407e-04 beta[77]
   - 4.04491e-05 beta[78] - 1.47735e-05 beta[79]
   + 0.0260820614968662 beta[80] + 0.00371600452412509 beta[81]
   + 0.00216276485499579 beta[82] + 0.000915028 beta[83]
   + 3.7105233348883076e-04 beta[84] + 1.6251368199844649e-04 beta[85]
   + 7.87927e-05 beta[86] + 4.14572e-05 beta[87]
   - 0.0973318205171518 beta[88] - 0.00440484770823468 beta[89]
   - 0.00174112458503047 beta[90] - 7.3952840774375579e-04 beta[91]
   - 3.1878688061714723e-04 beta[92] - 1.5485674891892951e-04 beta[93]
   - 8.47556e-05 beta[94] - 5.04467e-05 beta[95]
   - 0.00721272616536586 beta[96] - 0.00135223670752727 beta[97]
   - 5.1880978903725194e-04 beta[98] - 2.955405078792802e-04 beta[99]
   - 0.000195813 beta[100] - 1.393672258722678e-04 beta[101]
   - 1.0337913618040289e-04 beta[102] - 7.89733e-05 beta[103]
   + 0.00452282756894152 beta[104] + 0.00053311 beta[105]
   + 2.6735111245087395e-04 beta[106] + 0.000186103 beta[107]
   + 0.000134383 beta[108] + 9.99622e-05 beta[109] + 7.64749e-05 beta[110]
   + 5.99624e-05 beta[111] - 4.8467366590376797e-04 beta[112]
   + 2.8648855034959174e-04 beta[113] + 5.29448e-05 beta[114]
   - 5.7711e-06 beta[115] - 1.64249e-05 beta[116] - 1.65587e-05 beta[117]
   - 1.47908e-05 beta[118] - 1.29361e-05 beta[119]
   - 0.00135072094924103 beta[120] - 3.8455575612524935e-04 beta[121]
   - 2.2326170147025798e-04 beta[122] - 1.4363433075322623e-04 beta[123]
   - 9.7354e-05 beta[124] - 6.97714e-05 beta[125] - 5.21879e-05 beta[126]
   - 4.0263e-05 beta[127] + 1.22239e-05 beta[128] - 9.66399e-05 beta[129]
   + 0.000139734 beta[130] + 1.4610735124908036e-04 beta[131]
   + 0.000116334 beta[132] + 8.9835e-05 beta[133] + 7.02934e-05 beta[134]
   + 5.61293e-05 beta[135] - 5.7213689136984599e-04 beta[136]
   + 2.1106554697173884e-04 beta[137] + 3.70479e-05 beta[138]
   - 2.18092e-05 beta[139] - 3.46156e-05 beta[140] - 3.38167e-05 beta[141]
   - 2.98787e-05 beta[142] - 2.57683e-05 beta[143]
   + 0.00428949222274366 beta[144] + 3.8367260130610554e-04 beta[145]
   - 5.1713e-05 beta[146] - 7.07816e-05 beta[147] - 4.91151e-05 beta[148]
   - 3.21207e-05 beta[149] - 2.14631e-05 beta[150] - 1.48145e-05 beta[151]
   - 0.00346744921806592 beta[152] - 6.1327810530876906e-04 beta[153]
   - 4.05928e-05 beta[154] + 5.56781e-05 beta[155] + 6.08423e-05 beta[156]
   + 5.0679e-05 beta[157] + 4.02083e-05 beta[158] + 3.18534e-05 beta[159]
   - 0.00287569398414705 beta[160] - 2.95419e-05 beta[161]
   + 3.59536e-05 beta[162] - 3.69056e-06 beta[163] - 2.12226e-05 beta[164]
   - 2.53175e-05 beta[165] - 2.43263e-05 beta[166] - 2.18048e-05 beta[167]
   + 0.00476420058947617 beta[168] + 4.3331768673887802e-04 beta[169]
   + 2.41307e-06 beta[170] - 3.26832e-05 beta[171] - 2.2512e-05 beta[172]
   - 1.17058e-05 beta[173] - 4.71372e-06 beta[174] - 6.3284e-07 beta[175]
   - 3.8301018289505742e-04 beta[176] - 1.1512814578729485e-04 beta[177]
   + 3.42883e-05 beta[178] + 5.21508e-05 beta[179] + 4.30055e-05 beta[180]
   + 3.16976e-05 beta[181] + 2.2716e-05 beta[182] + 1.61913e-05 beta[183]
   - 0.00293984574185394 beta[184] - 2.5417061912005916e-04 beta[185]
   - 6.89471e-05 beta[186] - 3.884e-05 beta[187] - 2.76208e-05 beta[188]
   - 2.09963e-05 beta[189] - 1.63189e-05 beta[190] - 1.27881e-05 beta[191]
   - 0.0301724466519035 beta[192] - 0.00211092095844746 beta[193]
   + 0.0154433048999585 beta[194] + 0.00441694444882642 beta[195]
   - 0.0101841653300322 beta[196] - 0.00529819344809207 beta[197]
   + 0.00646869512365022 beta[198] + 0.00483286625691388 beta[199]
   - 0.00797554522648072 beta[200] + 9.6145585721199285e-04 beta[201]
   + 0.00439180638687931 beta[202] - 0.00156797037749993 beta[203]
   - 0.00464497101349348 beta[204] + 9.2590540712809944e-04 beta[205]
   + 0.00481721077947995 beta[206] + 1.3657213545741894e-04 beta[207]
   + 0.00273074113751919 beta[208] - 6.2034632164599914e-04 beta[209]
   - 0.00229884348846727 beta[210] + 7.79929e-06 beta[211]
   + 0.00249417465857083 beta[212] + 0.00130140944077859 beta[213]
   - 0.00162530842634677 beta[214] - 0.00188001301854332 beta[215]
   + 0.00608009197887908 beta[216] + 9.93658e-05 beta[217]
   - 0.00248128871462336 beta[218] + 8.3145961384800118e-04 beta[219]
   + 0.00225052116560967 beta[220] - 0.00143035870955099 beta[221]
   - 0.0032117946590253 beta[222] + 7.0574317597891893e-04 beta[223]
   + 0.00666310896640405 beta[224] + 8.5547942202649245e-04 beta[225]
   - 0.00317885779274197 beta[226] - 0.00163009416688023 beta[227]
   + 0.00124190382345757 beta[228] + 0.00127175691577516 beta[229]
   + 3.21006e-05 beta[230] + 6.26576e-06 beta[231] - 7.98318e-05 beta[232]
   - 3.4803333684053743e-04 beta[233] - 2.7850634235975619e-04 beta[234]
   + 3.6940469634642203e-04 beta[235] + 9.2342111450303434e-04 beta[236]
   + 5.4069653986636062e-04 beta[237] - 6.0860820103549973e-04 beta[238]
   - 0.00127744733253854 beta[239] - 0.00611911409202556 beta[240]
   - 6.706657048469823e-04 beta[241] + 0.00309008118911333 beta[242]
   + 0.00122246513154937 beta[243] - 0.00214766658442446 beta[244]
   - 0.00194548514178252 beta[245] + 7.245581523163036e-04 beta[246]
   + 0.00169435196296954 beta[247] - 0.00192918575363964 beta[248]
   + 3.0318440255047713e-04 beta[249] + 0.00105215552382353 beta[250]
   - 5.6750420802657755e-04 beta[251] - 0.00121265863194065 beta[252]
   + 0.000587245 beta[253] + 0.00181233946296809 beta[254]
   + 2.9317949840658848e-04 beta[255] + 0.00273969344014958 beta[256]
   + 4.3173071744386773e-04 beta[257] - 0.00131265452424109 beta[258]
   - 5.5834780916870399e-04 beta[259] + 0.00110510086478055 beta[260]
   + 9.0249423523407733e-04 beta[261] - 9.6872649407363047e-04 beta[262]
   - 0.00159799718845726 beta[263] + 1.8593953991623036e-04 beta[264]
   - 0.0003325 beta[265] - 2.633823509439654e-04 beta[266]
   + 3.6292133125342529e-04 beta[267] + 2.9558259048412944e-04 beta[268]
   - 5.0380757221657653e-04 beta[269] - 5.2208026577574556e-04 beta[270]
   + 5.9400344124591466e-04 beta[271] - 3.6609967403172734e-04 beta[272]
   + 4.2149e-05 beta[273] + 3.5178247815149764e-04 beta[274]
   + 9.82008e-05 beta[275] - 3.6628357363756596e-04 beta[276]
   - 1.8541339838428329e-04 beta[277] + 5.0587576497378812e-04 beta[278]
   + 0.000437849 beta[279] + 6.3383733635991881e-04 beta[280]
   - 8.87468e-05 beta[281] - 4.3479063518301128e-04 beta[282]
   + 8.7592e-06 beta[283] + 0.000381708 beta[284] + 4.28438e-05 beta[285]
   - 0.000423269 beta[286] - 2.3782954197270641e-04 beta[287]
   - 0.29858205666189 beta[288] + 8.65867e-05 beta[289]
   + 0.0680054197263078 beta[290] + 7.38144e-11 beta[291]
   + weighted_residual[1] = -0.2625450743804912
 R592: - 0.2533759945949692 beta[0] - 0.00632902631253721 beta[1]
   + 0.00447705260104643 beta[2] + 0.00194481289935967 beta[3]
   + 5.2575913647737388e-04 beta[4] + 6.35463e-05 beta[5]
   - 4.54926e-05 beta[6] - 5.42457e-05 beta[7] + 0.1183251012626602 beta[8]
   - 0.00764061491061003 beta[9] - 0.00441856654993485 beta[10]
   - 0.00135577 beta[11] - 3.3279464129957228e-04 beta[12]
   - 5.09863e-05 beta[13] + 1.22526e-05 beta[14] + 1.9447e-05 beta[15]
   + 0.0832737954374639 beta[16] + 0.0295069634929218 beta[17]
   + 0.00556583412823369 beta[18] + 0.00104717344337146 beta[19]
   + 2.4063553279745701e-04 beta[20] + 8.94489e-05 beta[21]
   + 5.17562e-05 beta[22] + 3.54692e-05 beta[23]
   - 0.2419821831572178 beta[24] - 0.0404494778776204 beta[25]
   - 0.00604861835457463 beta[26] - 0.00104067802091289 beta[27]
   - 2.9992524185663757e-04 beta[28] - 1.6515647280868125e-04 beta[29]
   - 1.1460938481209362e-04 beta[30] - 8.17634e-05 beta[31]
   + 0.3002054828200972 beta[32] + 0.0272297058483131 beta[33]
   + 0.00274140447573397 beta[34] + 0.000417775 beta[35]
   + 2.0179047361239299e-04 beta[36] + 1.5607585586645219e-04 beta[37]
   + 1.1841212995693102e-04 beta[38] + 8.71267e-05 beta[39]
   - 0.187705222971162 beta[40] + 0.00475699503528152 beta[41]
   + 0.00381345896641099 beta[42] + 0.00111861489645525 beta[43]
   + 2.510474962431482e-04 beta[44] + 2.31248e-05 beta[45]
   - 2.85787e-05 beta[46] - 3.59031e-05 beta[47]
   - 0.0927920927465607 beta[48] - 0.0379868609464831 beta[49]
   - 0.00991573609853481 beta[50] - 0.00276479239172515 beta[51]
   - 8.6067518625892938e-04 beta[52] - 3.0836373016062524e-04 beta[53]
   - 1.2628337496781457e-04 beta[54] - 5.64977e-05 beta[55]
   + 0.1804662032387802 beta[56] + 0.0433669702722367 beta[57]
   + 0.0114132381833783 beta[58] + 0.00343779675001383 beta[59]
   + 0.00123774094348498 beta[60] + 5.3531023871359348e-04 beta[61]
   + 2.6805650124708434e-04 beta[62] + 1.4875639737999135e-04 beta[63]
   + 0.2183427037084772 beta[64] - 0.00284212296316788 beta[65]
   - 0.00593654337933211 beta[66] - 0.00249560649270612 beta[67]
   - 0.00110138142471258 beta[68] - 5.6014920145823542e-04 beta[69]
   - 3.182601132302584e-04 beta[70] - 1.9531085561675865e-04 beta[71]
   - 0.6855884930865283 beta[72] - 0.0538046378423346 beta[73]
   - 0.00395829374399401 beta[74] + 0.000191131 beta[75]
   + 4.4109039537120799e-04 beta[76] + 3.4273852158943542e-04 beta[77]
   + 2.4207442253759175e-04 beta[78] + 1.7018934968447325e-04 beta[79]
   + 0.6737961564974837 beta[80] + 0.0771019246002029 beta[81]
   + 0.0116776784184069 beta[82] + 0.00226990095935275 beta[83]
   + 4.5010048637975119e-04 beta[84] + 3.01852e-05 beta[85]
   - 6.66069e-05 beta[86] - 8.04332e-05 beta[87]
   - 0.3014681829456874 beta[88] - 0.0557401915903596 beta[89]
   - 0.0126342108049644 beta[90] - 0.00353367789199582 beta[91]
   - 0.00112691550239818 beta[92] - 3.8604456975902841e-04 beta[93]
   - 1.3163711908235795e-04 beta[94] - 3.68117e-05 beta[95]
   + 0.00960975432776205 beta[96] - 6.8005877945928541e-04 beta[97]
   - 5.1252025090735938e-04 beta[98] - 2.6948812608664288e-04 beta[99]
   - 1.6523146102989718e-04 beta[100] - 1.1736465833073396e-04 beta[101]
   - 9.07068e-05 beta[102] - 7.30942e-05 beta[103]
   + 0.00157823777618981 beta[104] + 9.5568944162157732e-04 beta[105]
   + 3.7510519368778741e-04 beta[106] + 1.8161129696058536e-04 beta[107]
   + 0.0001083 beta[108] + 7.49822e-05 beta[109] + 5.68029e-05 beta[110]
   + 4.52905e-05 beta[111] - 0.00726240283736347 beta[112]
   - 2.3896056431519367e-04 beta[113] + 7.82761e-05 beta[114]
   + 4.54018e-05 beta[115] + 2.10343e-05 beta[116] + 1.00545e-05 beta[117]
   + 4.95771e-06 beta[118] + 2.2731e-06 beta[119]
   + 0.00130529321262211 beta[120] - 0.00124148479525776 beta[121]
   - 6.1093875208329668e-04 beta[122] - 2.9997975987141554e-04 beta[123]
   - 1.6539038648126405e-04 beta[124] - 1.0231860904113453e-04 beta[125]
   - 6.9316e-05 beta[126] - 5.01069e-05 beta[127]
   + 0.0082628410042609 beta[128] + 0.00202409623876551 beta[129]
   + 7.3805847586307604e-04 beta[130] + 0.000362815 beta[131]
   + 2.121406367973529e-04 beta[132] + 0.000138494 beta[133]
   + 9.75307e-05 beta[134] + 7.25319e-05 beta[135]
   - 0.00919832756679649 beta[136] - 9.9319877851415249e-04 beta[137]
   - 2.694231839297811e-04 beta[138] - 1.5231361294809574e-04 beta[139]
   - 1.0992243615291322e-04 beta[140] - 8.45304e-05 beta[141]
   - 6.68073e-05 beta[142] - 5.39217e-05 beta[143]
   - 0.00495532060642384 beta[144] - 0.00181945972425154 beta[145]
   - 0.000591324 beta[146] - 2.1830168084740689e-04 beta[147]
   - 8.60146e-05 beta[148] - 3.26685e-05 beta[149] - 9.23915e-06 beta[150]
   + 1.58056e-06 beta[151] + 0.0178240773049838 beta[152]
   + 0.00385534624827672 beta[153] + 0.00122607299385923 beta[154]
   + 5.142596080120296e-04 beta[155] + 2.5791715474849356e-04 beta[156]
   + 0.000145395 beta[157] + 8.86576e-05 beta[158] + 5.70776e-05 beta[159]
   - 0.00768303875064619 beta[160] - 0.00218903580860928 beta[161]
   - 9.5696858631857051e-04 beta[162] - 0.000496337 beta[163]
   - 0.0002898 beta[164] - 0.000184934 beta[165]
   - 1.259892293049923e-04 beta[166] - 9.00699e-05 beta[167]
   - 0.0123510420525897 beta[168] - 0.00160758496126569 beta[169]
   - 7.42123e-05 beta[170] + 1.4083066477270104e-04 beta[171]
   + 1.47021521583557e-04 beta[172] + 1.2242319423606755e-04 beta[173]
   + 9.81524e-05 beta[174] + 7.87622e-05 beta[175]
   + 0.015077399869069 beta[176] + 0.00347037327302056 beta[177]
   + 9.6227125884745996e-04 beta[178] + 2.9028180794592011e-04 beta[179]
   + 7.93291e-05 beta[180] + 6.17585e-06 beta[181] - 2.01819e-05 beta[182]
   - 2.90974e-05 beta[183] - 0.00383997763635515 beta[184]
   - 0.00253018784878969 beta[185] - 0.00110774320138982 beta[186]
   - 5.0040032764437075e-04 beta[187] - 2.4105067832917693e-04 beta[188]
   - 1.2172580597841761e-04 beta[189] - 6.25103e-05 beta[190]
   - 3.12137e-05 beta[191] - 0.00288972697340022 beta[192]
   - 0.00172162038481364 beta[193] + 9.3162642862657094e-04 beta[194]
   + 0.00233817294207666 beta[195] - 3.48928e-05 beta[196]
   - 0.0026874979377812 beta[197] - 7.3675166534946195e-04 beta[198]
   + 0.00292625305352244 beta[199] - 0.00504450833922073 beta[200]
   + 1.8693635207790661e-04 beta[201] + 0.00275255832722909 beta[202]
   - 7.10979e-05 beta[203] - 0.00221677737271794 beta[204]
   - 4.61611e-05 beta[205] + 0.00192051666338986 beta[206]
   + 4.53316e-05 beta[207] - 0.00585244325426347 beta[208]
   + 2.2030640434997478e-04 beta[209] + 0.00288731179648903 beta[210]
   - 5.0658452294564515e-04 beta[211] - 0.00235670688480447 beta[212]
   + 6.8347612210448844e-04 beta[213] + 0.00236111650978184 beta[214]
   - 0.00060665 beta[215] + 0.00139167113264916 beta[216]
   - 8.82944e-05 beta[217] - 6.7215070182581572e-04 beta[218]
   + 2.8309226815139473e-04 beta[219] + 0.000693604 beta[220]
   - 3.8490520981841395e-04 beta[221] - 9.5782876806707097e-04 beta[222]
   + 2.593113741027532e-04 beta[223] + 0.00905118780748821 beta[224]
   + 2.9885079501775847e-04 beta[225] - 0.00458412585336172 beta[226]
   - 5.6401060147577542e-04 beta[227] + 0.00338299796887804 beta[228]
   + 7.5286936893175524e-04 beta[229] - 0.00267475577692063 beta[230]
   - 8.3492281166863756e-04 beta[231] + 0.00209989558352923 beta[232]
   + 2.0470761102531982e-04 beta[233] - 9.2809772273213761e-04 beta[234]
   - 2.4049744140711295e-04 beta[235] + 5.4092867503989495e-04 beta[236]
   + 2.3603778470545304e-04 beta[237] - 2.3632961761168743e-04 beta[238]
   - 1.3369346573883606e-04 beta[239] - 0.00739750473674541 beta[240]
   - 0.000718705 beta[241] + 0.00357875773418772 beta[242]
   + 0.00108291933921468 beta[243] - 0.00243404123440225 beta[244]
   - 0.00133070740120667 beta[245] + 0.00160327 beta[246]
   + 0.00134941897703058 beta[247] + 0.000475592 beta[248]
   + 0.000127883 beta[249] - 2.7895847177552218e-04 beta[250]
   - 2.8772222654576551e-04 beta[251] + 1.6841184617489197e-04 beta[252]
   + 4.6343563781691582e-04 beta[253] + 8.02107e-05 beta[254]
   - 4.9144843278652885e-04 beta[255] + 0.00489594949531055 beta[256]
   + 0.000521444 beta[257] - 0.00223322425177996 beta[258]
   - 6.2298722933166702e-04 beta[259] + 0.00143770272042751 beta[260]
   + 5.5560048905244942e-04 beta[261] - 0.00107020323017828 beta[262]
   - 4.6636578502346051e-04 beta[263] - 0.00274163376292513 beta[264]
   - 4.7815588843175272e-04 beta[265] + 0.00112620038254704 beta[266]
   + 5.7240174414354707e-04 beta[267] - 5.2448110665838182e-04 beta[268]
   - 4.9941535257243144e-04 beta[269] + 1.3052119923609695e-04 beta[270]
   + 3.0673678615636928e-04 beta[271] - 0.00269682271290104 beta[272]
   + 3.7204312457419521e-04 beta[273] + 0.00149920797168404 beta[274]
   - 0.000500703 beta[275] - 0.0013493856973208 beta[276]
   + 5.5815018317549895e-04 beta[277] + 0.00144426187770775 beta[278]
   - 4.9027234129663303e-04 beta[279] - 0.00130773848522607 beta[280]
   - 1.4412324803839152e-04 beta[281] + 6.9512732829918539e-04 beta[282]
   + 2.7217326846785755e-04 beta[283] - 5.6558585349468342e-04 beta[284]
   - 4.8828762505443519e-04 beta[285] + 3.676284314011939e-04 beta[286]
   + 6.740652595756733e-04 beta[287] - 0.31797074561487 beta[288]
   + 0.000358772 beta[289] + 0.073940998287532 beta[290]
   - 4.69783e-09 beta[291] + weighted_residual[2] = -0.267568911653786
 R593: - 0.00136255339832303 beta[0] + 1.2417638638684281e-04 beta[1]
   + 8.10336e-05 beta[2] + 3.05521e-05 beta[3] + 1.13643e-05 beta[4]
   + 4.70856e-06 beta[5] + 2.27972e-06 beta[6] + 1.27607e-06 beta[7]
   - 5.3074831875221662e-04 beta[8] - 2.0035128662332369e-04 beta[9]
   - 6.65027e-05 beta[10] - 2.21082e-05 beta[11] - 8.16099e-06 beta[12]
   - 3.5269e-06 beta[13] - 1.79581e-06 beta[14] - 1.04076e-06 beta[15]
   + 0.0025809162530166 beta[16] + 0.000309171 beta[17]
   + 5.30935e-05 beta[18] + 1.22975e-05 beta[19] + 4.01636e-06 beta[20]
   + 1.80195e-06 beta[21] + 9.89128e-07 beta[22] + 6.02184e-07 beta[23]
   - 0.00300116294847719 beta[24] - 3.3621948047568573e-04 beta[25]
   - 4.04198e-05 beta[26] - 4.74486e-06 beta[27] - 4.73617e-07 beta[28]
   - 4.49981e-08 beta[29] - 1.67951e-08 beta[30] - 9.55589e-09 beta[31]
   + 0.00205108232760765 beta[32] + 2.2119361483913247e-04 beta[33]
   + 1.48325e-05 beta[34] - 3.11545e-06 beta[35] - 2.81049e-06 beta[36]
   - 1.68358e-06 beta[37] - 1.01635e-06 beta[38] - 6.49942e-07 beta[39]
   - 9.1527960997872526e-04 beta[40] - 2.00906e-05 beta[41]
   + 2.33258e-05 beta[42] + 1.25809e-05 beta[43] + 6.12057e-06 beta[44]
   + 3.25321e-06 beta[45] + 1.90626e-06 beta[46] + 1.2006e-06 beta[47]
   - 4.0570783882643013e-04 beta[48] - 0.000190069 beta[49]
   - 5.77546e-05 beta[50] - 1.98212e-05 beta[51] - 8.16776e-06 beta[52]
   - 4.02088e-06 beta[53] - 2.25993e-06 beta[54] - 1.38532e-06 beta[55]
   + 0.0013616895634927 beta[56] + 2.8931934603154685e-04 beta[57]
   + 6.64918e-05 beta[58] + 1.90445e-05 beta[59] + 6.96164e-06 beta[60]
   + 3.16138e-06 beta[61] + 1.67904e-06 beta[62] + 9.87548e-07 beta[63]
   - 6.15916e-05 beta[64] - 1.1793421743927501e-04 beta[65]
   - 3.01763e-05 beta[66] - 6.73264e-06 beta[67] - 1.59571e-06 beta[68]
   - 4.12702e-07 beta[69] - 1.00659e-07 beta[70] - 7.91275e-09 beta[71]
   - 0.00295686869767775 beta[72] - 2.7108931081640253e-04 beta[73]
   - 4.41856e-05 beta[74] - 1.43662e-05 beta[75] - 6.50493e-06 beta[76]
   - 3.42054e-06 beta[77] - 1.98406e-06 beta[78] - 1.23568e-06 beta[79]
   + 0.00444978554606568 beta[80] + 0.000559854 beta[81]
   + 1.1051371348921868e-04 beta[82] + 3.33763e-05 beta[83]
   + 1.34709e-05 beta[84] + 6.56055e-06 beta[85] + 3.62469e-06 beta[86]
   + 2.18351e-06 beta[87] - 0.00317159745520268 beta[88]
   - 5.0639377756567239e-04 beta[89] - 1.1680926810444386e-04 beta[90]
   - 3.6737e-05 beta[91] - 1.47119e-05 beta[92] - 7.05121e-06 beta[93]
   - 3.84001e-06 beta[94] - 2.28638e-06 beta[95] - 2.11861e-05 beta[96]
   - 2.18244e-06 beta[97] + 6.05838e-07 beta[98] + 6.75988e-07 beta[99]
   + 4.48909e-07 beta[100] + 2.70086e-07 beta[101] + 1.60082e-07 beta[102]
   + 9.68627e-08 beta[103] + 1.70521e-05 beta[104] + 3.82228e-06 beta[105]
   + 6.15075e-07 beta[106] - 1.10232e-08 beta[107] - 1.1027e-07 beta[108]
   - 1.04682e-07 beta[109] - 8.40936e-08 beta[110] - 6.64155e-08 beta[111]
   - 4.13943e-07 beta[112] - 1.87735e-06 beta[113] - 7.29001e-07 beta[114]
   - 2.52714e-07 beta[115] - 6.31603e-08 beta[116] + 1.53337e-08 beta[117]
   + 4.71964e-08 beta[118] + 5.83358e-08 beta[119] - 1.19337e-05 beta[120]
   - 3.21855e-06 beta[121] - 8.99099e-07 beta[122] - 3.39323e-07 beta[123]
   - 1.8486e-07 beta[124] - 1.33586e-07 beta[125] - 1.10573e-07 beta[126]
   - 9.58032e-08 beta[127] + 1.79342e-05 beta[128] + 7.55835e-06 beta[129]
   + 2.64231e-06 beta[130] + 1.09157e-06 beta[131] + 5.32304e-07 beta[132]
   + 2.96644e-07 beta[133] + 1.83426e-07 beta[134] + 1.22724e-07 beta[135]
   - 2.79004e-05 beta[136] - 7.99459e-06 beta[137] - 2.67038e-06 beta[138]
   - 1.0653e-06 beta[139] - 4.82011e-07 beta[140] - 2.33566e-07 beta[141]
   - 1.14849e-07 beta[142] - 5.36123e-08 beta[143] + 7.04801e-06 beta[144]
   - 2.80572e-07 beta[145] - 2.00962e-07 beta[146] - 1.77498e-07 beta[147]
   - 1.70602e-07 beta[148] - 1.59093e-07 beta[149] - 1.45565e-07 beta[150]
   - 1.31947e-07 beta[151] + 5.17515e-05 beta[152] + 1.43187e-05 beta[153]
   + 4.78104e-06 beta[154] + 2.07908e-06 beta[155] + 1.11218e-06 beta[156]
   + 6.86292e-07 beta[157] + 4.67001e-07 beta[158] + 3.40277e-07 beta[159]
   - 6.59167e-05 beta[160] - 1.82375e-05 beta[161] - 6.71034e-06 beta[162]
   - 3.01021e-06 beta[163] - 1.57377e-06 beta[164] - 9.24458e-07 beta[165]
   - 5.92105e-07 beta[166] - 4.04384e-07 beta[167] + 2.74128e-06 beta[168]
   + 4.64158e-06 beta[169] + 2.96277e-06 beta[170] + 1.61451e-06 beta[171]
   + 8.94234e-07 beta[172] + 5.21166e-07 beta[173] + 3.18754e-07 beta[174]
   + 2.02328e-07 beta[175] + 5.79931e-05 beta[176] + 1.37821e-05 beta[177]
   + 4.07022e-06 beta[178] + 1.54887e-06 beta[179] + 7.47421e-07 beta[180]
   + 4.376e-07 beta[181] + 2.9519e-07 beta[182] + 2.19287e-07 beta[183]
   - 6.7563e-05 beta[184] - 2.28089e-05 beta[185] - 9.08741e-06 beta[186]
   - 4.24045e-06 beta[187] - 2.27318e-06 beta[188] - 1.36371e-06 beta[189]
   - 8.92954e-07 beta[190] - 6.25184e-07 beta[191] - 3.80053e-05 beta[192]
   + 2.93833e-06 beta[193] + 2.51553e-05 beta[194] + 1.51926e-06 beta[195]
   - 2.37744e-05 beta[196] - 8.78261e-06 beta[197] + 2.03291e-05 beta[198]
   + 1.52335e-05 beta[199] + 1.61071e-06 beta[200] - 5.89471e-06 beta[201]
   - 5.57292e-06 beta[202] + 4.52052e-06 beta[203] + 8.07102e-06 beta[204]
   - 1.10203e-06 beta[205] - 7.94425e-06 beta[206] - 1.68912e-06 beta[207]
   + 4.69375e-05 beta[208] + 6.06803e-06 beta[209] - 2.1127e-05 beta[210]
   - 7.11332e-06 beta[211] + 1.4129e-05 beta[212] + 7.629e-06 beta[213]
   - 1.06039e-05 beta[214] - 8.7415e-06 beta[215] - 1.64814e-05 beta[216]
   + 1.10989e-07 beta[217] + 8.6599e-06 beta[218] - 1.26152e-07 beta[219]
   - 7.78264e-06 beta[220] - 1.25718e-06 beta[221] + 7.14761e-06 beta[222]
   + 3.67181e-06 beta[223] - 5.20313e-05 beta[224] - 6.03568e-06 beta[225]
   + 2.38436e-05 beta[226] + 7.94039e-06 beta[227] - 1.45879e-05 beta[228]
   - 7.42548e-06 beta[229] + 9.52137e-06 beta[230] + 5.46824e-06 beta[231]
   + 1.9662e-05 beta[232] + 3.84406e-06 beta[233] - 7.98556e-06 beta[234]
   - 4.67744e-06 beta[235] + 3.54391e-06 beta[236] + 4.11547e-06 beta[237]
   - 7.55333e-07 beta[238] - 2.57594e-06 beta[239] + 4.0708e-05 beta[240]
   + 1.43775e-06 beta[241] - 2.05812e-05 beta[242] - 2.55787e-06 beta[243]
   + 1.52029e-05 beta[244] + 3.04315e-06 beta[245] - 1.26374e-05 beta[246]
   - 3.37845e-06 beta[247] + 5.2711e-07 beta[248] - 1.49284e-06 beta[249]
   - 1.11957e-06 beta[250] + 2.07898e-06 beta[251] + 2.85406e-06 beta[252]
   - 9.21203e-07 beta[253] - 3.82201e-06 beta[254] - 1.21284e-06 beta[255]
   - 3.47366e-05 beta[256] + 2.34925e-07 beta[257] + 1.81981e-05 beta[258]
   - 2.80146e-07 beta[259] - 1.58286e-05 beta[260] - 1.44731e-06 beta[261]
   + 1.49229e-05 beta[262] + 4.4619e-06 beta[263] - 2.6437e-05 beta[264]
   - 2.59936e-06 beta[265] + 1.30008e-05 beta[266] + 4.45427e-06 beta[267]
   - 8.20241e-06 beta[268] - 4.91708e-06 beta[269] + 4.98522e-06 beta[270]
   + 4.06968e-06 beta[271] + 4.36672e-05 beta[272] + 1.90598e-06 beta[273]
   - 2.26652e-05 beta[274] - 4.07071e-06 beta[275] + 1.70031e-05 beta[276]
   + 5.96462e-06 beta[277] - 1.32733e-05 beta[278] - 7.11731e-06 beta[279]
   + 3.8224e-05 beta[280] + 4.55881e-06 beta[281] - 1.72027e-05 beta[282]
   - 5.46461e-06 beta[283] + 1.07914e-05 beta[284] + 5.03816e-06 beta[285]
   - 7.57559e-06 beta[286] - 4.27516e-06 beta[287]
   - 0.00175061600003801 beta[288] - 4e-08 beta[289]
   + 0.000641999 beta[290] + weighted_residual[3] = -0.00133795200133561
 R594: 0.00304410179879255 beta[0] + 8.88645e-05 beta[1]
   - 7.97424e-05 beta[2] - 1.8253e-05 beta[3] + 1.65322e-05 beta[4]
   + 2.69511e-05 beta[5] + 2.71109e-05 beta[6] + 2.40072e-05 beta[7]
   - 0.00303054959861271 beta[8] - 1.4953366628933651e-04 beta[9]
   - 2.62637e-05 beta[10] - 4.61046e-05 beta[11] - 5.0241e-05 beta[12]
   - 4.4334e-05 beta[13] - 3.62558e-05 beta[14] - 2.89406e-05 beta[15]
   + 0.00188476736681764 beta[16] + 0.000228378 beta[17]
   + 0.00016643 beta[18] + 1.2871037552292242e-04 beta[19]
   + 9.27553e-05 beta[20] + 6.5845e-05 beta[21] + 4.72933e-05 beta[22]
   + 3.46949e-05 beta[23] - 7.6398574069713732e-04 beta[24]
   - 4.2356658047415507e-04 beta[25] - 3.0728548861796989e-04 beta[26]
   - 1.9974030818412786e-04 beta[27] - 1.2694839236932279e-04 beta[28]
   - 8.23666e-05 beta[29] - 5.53641e-05 beta[30] - 3.86172e-05 beta[31]
   + 9.8425712549143896e-04 beta[32] + 0.000756613 beta[33]
   + 4.4763157299926304e-04 beta[34] + 0.000256149 beta[35]
   + 1.5015977918088688e-04 beta[36] + 9.21271e-05 beta[37]
   + 5.9387e-05 beta[38] + 4.00571e-05 beta[39]
   - 8.9336673225304253e-04 beta[40] - 9.6295329903739457e-04 beta[41]
   - 0.000539557 beta[42] - 2.8669239992992757e-04 beta[43]
   - 0.000158489 beta[44] - 9.31468e-05 beta[45] - 5.81388e-05 beta[46]
   - 3.82119e-05 beta[47] - 3.9745560139081704e-04 beta[48]
   + 9.2292582136832557e-04 beta[49] + 5.4926117043913036e-04 beta[50]
   + 2.8402237542931794e-04 beta[51] + 1.5165756986164e-04 beta[52]
   + 8.6508e-05 beta[53] + 5.26931e-05 beta[54] + 3.39199e-05 beta[55]
   + 0.00125298769006577 beta[56] - 8.606957763479528e-04 beta[57]
   - 0.000529076 beta[58] - 2.6907045279394443e-04 beta[59]
   - 1.4077213419208881e-04 beta[60] - 7.8765e-05 beta[61]
   - 4.71002e-05 beta[62] - 2.97612e-05 beta[63]
   - 0.00193229292455577 beta[64] + 8.2697450688784535e-04 beta[65]
   + 0.000519688 beta[66] + 2.5861218391078078e-04 beta[67]
   + 1.3223726404943716e-04 beta[68] + 7.2455e-05 beta[69]
   + 4.24393e-05 beta[70] + 2.62343e-05 beta[71]
   + 0.00384695915144562 beta[72] - 6.8085530533279481e-04 beta[73]
   - 4.9752077630978164e-04 beta[74] - 2.4403867299608098e-04 beta[75]
   - 1.2110540420768538e-04 beta[76] - 6.44507e-05 beta[77]
   - 3.67356e-05 beta[78] - 2.21055e-05 beta[79]
   - 0.005372401416599 beta[80] + 5.8393358574493348e-04 beta[81]
   + 4.7458726456527101e-04 beta[82] + 2.2643462972266569e-04 beta[83]
   + 1.0845683561619846e-04 beta[84] + 5.58964e-05 beta[85]
   + 3.09531e-05 beta[86] + 1.81104e-05 beta[87]
   + 0.00450519312662045 beta[88] - 7.8659922493340417e-04 beta[89]
   - 5.0132661315607785e-04 beta[90] - 2.2301953878985092e-04 beta[91]
   - 1.0249241353141401e-04 beta[92] - 5.1288e-05 beta[93]
   - 2.76968e-05 beta[94] - 1.57979e-05 beta[95]
   - 1.7408615448216702e-04 beta[96] - 5.99841e-05 beta[97]
   - 3.5607e-05 beta[98] - 2.31654e-05 beta[99] - 1.52114e-05 beta[100]
   - 9.97159e-06 beta[101] - 6.48707e-06 beta[102] - 4.14452e-06 beta[103]
   - 3.26564e-05 beta[104] - 5.18048e-06 beta[105] - 1.16707e-06 beta[106]
   - 6.80223e-07 beta[107] - 8.27821e-07 beta[108] - 1.0164e-06 beta[109]
   - 1.12916e-06 beta[110] - 1.16557e-06 beta[111] + 6.95359e-05 beta[112]
   + 1.68763e-05 beta[113] + 8.28759e-06 beta[114] + 5.02389e-06 beta[115]
   + 3.19773e-06 beta[116] + 2.06656e-06 beta[117] + 1.33907e-06 beta[118]
   + 8.59827e-07 beta[119] + 3.75908e-05 beta[120] + 1.64077e-05 beta[121]
   + 9.86686e-06 beta[122] + 6.62019e-06 beta[123] + 4.73583e-06 beta[124]
   + 3.5448e-06 beta[125] + 2.73748e-06 beta[126] + 2.1588e-06 beta[127]
   - 1.69904e-05 beta[128] - 5.11724e-06 beta[129] - 3.20511e-06 beta[130]
   - 1.96281e-06 beta[131] - 1.09622e-06 beta[132] - 5.40292e-07 beta[133]
   - 1.97244e-07 beta[134] + 1.0435e-08 beta[135] - 4.15312e-05 beta[136]
   - 2.02491e-05 beta[137] - 1.20782e-05 beta[138] - 7.72114e-06 beta[139]
   - 5.18159e-06 beta[140] - 3.62653e-06 beta[141] - 2.62742e-06 beta[142]
   - 1.95591e-06 beta[143] + 2.06934e-06 beta[144] + 4.73223e-06 beta[145]
   + 3.30375e-06 beta[146] + 1.65704e-06 beta[147] + 5.73131e-07 beta[148]
   - 3.26664e-08 beta[149] - 3.39309e-07 beta[150] - 4.75141e-07 beta[151]
   - 4.63647e-06 beta[152] + 3.62717e-06 beta[153] + 4.37103e-06 beta[154]
   + 3.43806e-06 beta[155] + 2.4864e-06 beta[156] + 1.77796e-06 beta[157]
   + 1.27915e-06 beta[158] + 9.27389e-07 beta[159] + 5.73919e-05 beta[160]
   + 1.49265e-05 beta[161] + 5.42168e-06 beta[162] + 3.19878e-06 beta[163]
   + 2.51576e-06 beta[164] + 2.14387e-06 beta[165] + 1.84107e-06 beta[166]
   + 1.56989e-06 beta[167] - 7.98714e-06 beta[168] - 4.82158e-06 beta[169]
   - 3.9107e-06 beta[170] - 3.12339e-06 beta[171] - 2.41956e-06 beta[172]
   - 1.83931e-06 beta[173] - 1.38267e-06 beta[174] - 1.03214e-06 beta[175]
   - 8.42721e-05 beta[176] - 2.8969e-05 beta[177] - 1.22519e-05 beta[178]
   - 6.41436e-06 beta[179] - 3.96741e-06 beta[180] - 2.73669e-06 beta[181]
   - 2.01497e-06 beta[182] - 1.54117e-06 beta[183] + 8.55569e-05 beta[184]
   + 3.11811e-05 beta[185] + 1.36356e-05 beta[186] + 6.971e-06 beta[187]
   + 4.01955e-06 beta[188] + 2.51988e-06 beta[189] + 1.6697e-06 beta[190]
   + 1.14826e-06 beta[191] + 0.00032339 beta[192] + 2.60475e-05 beta[193]
   - 1.7609914328753362e-04 beta[194] - 5.46803e-05 beta[195]
   + 0.00015158 beta[196] + 1.1583014987548435e-04 beta[197]
   - 9.58893e-05 beta[198] - 1.540943737537992e-04 beta[199]
   + 1.8321478483449005e-04 beta[200] + 5.17145e-05 beta[201]
   - 5.96713e-05 beta[202] - 5.77576e-05 beta[203] - 4.24922e-06 beta[204]
   + 1.64442e-05 beta[205] + 1.14904e-05 beta[206] + 1.55578e-05 beta[207]
   - 0.000293821 beta[208] - 7.89451e-05 beta[209]
   + 1.1225141981457964e-04 beta[210] + 1.0125125075075014e-04 beta[211]
   - 2.76498e-05 beta[212] - 7.573e-05 beta[213] - 3.21145e-06 beta[214]
   + 5.28419e-05 beta[215] - 1.07188e-05 beta[216] + 1.74748e-05 beta[217]
   + 1.41104e-05 beta[218] - 2.41773e-05 beta[219] - 3.16933e-05 beta[220]
   + 7.37421e-06 beta[221] + 2.7558e-05 beta[222] - 1.13295e-06 beta[223]
   + 1.4569487137558457e-04 beta[224] + 4.64164e-05 beta[225]
   - 5.00601e-05 beta[226] - 5.2381e-05 beta[227] + 1.69721e-05 beta[228]
   + 5.47766e-05 beta[229] + 1.39144e-05 beta[230] - 3.86308e-05 beta[231]
   - 1.2330451773348398e-04 beta[232] - 5.5398e-05 beta[233]
   + 2.71026e-05 beta[234] + 5.48689e-05 beta[235] + 1.08322e-05 beta[236]
   - 4.22443e-05 beta[237] - 3.52592e-05 beta[238] + 1.58196e-05 beta[239]
   + 7.94584e-05 beta[240] + 2.7386e-05 beta[241] - 1.40212e-05 beta[242]
   - 1.41199e-05 beta[243] - 2.94164e-06 beta[244] - 1.71031e-06 beta[245]
   + 5.36332e-06 beta[246] + 1.79729e-05 beta[247] + 6.24736e-05 beta[248]
   + 2.29684e-06 beta[249] - 4.22758e-05 beta[250] - 2.21496e-05 beta[251]
   + 2.3962e-05 beta[252] + 3.04973e-05 beta[253] - 5.18473e-06 beta[254]
   - 2.93072e-05 beta[255] - 9.94085e-05 beta[256] - 1.0073e-05 beta[257]
   + 5.18801e-05 beta[258] + 2.55789e-05 beta[259] - 2.29392e-05 beta[260]
   - 2.28593e-05 beta[261] + 4.32195e-06 beta[262] + 1.08545e-05 beta[263]
   - 5.18196e-05 beta[264] + 1.12088e-07 beta[265] + 2.55752e-05 beta[266]
   - 5.57237e-06 beta[267] - 3.13963e-05 beta[268] - 4.81496e-06 beta[269]
   + 3.04491e-05 beta[270] + 1.67189e-05 beta[271] + 5.8922e-05 beta[272]
   + 2.41029e-06 beta[273] - 2.88386e-05 beta[274] - 8.73696e-07 beta[275]
   + 2.76373e-05 beta[276] + 9.83612e-06 beta[277] - 1.88785e-05 beta[278]
   - 1.23352e-05 beta[279] + 7.33954e-05 beta[280] + 4.06154e-06 beta[281]
   - 3.67702e-05 beta[282] - 6.75416e-06 beta[283] + 2.53868e-05 beta[284]
   + 3.39697e-06 beta[285] - 2.81964e-05 beta[286] - 1.0794e-05 beta[287]
   + 0.00515173600003749 beta[288] - 4.94e-06 beta[289]
   - 0.00171294 beta[290] + weighted_residual[4] = 0.00382116400033976
 R595: - 0.00106514672033597 beta[0] - 2.749728626483261e-04 beta[1]
   - 5.1632853093619424e-04 beta[2] - 3.7027286835661366e-04 beta[3]
   - 1.9381023333223113e-04 beta[4] - 7.82574e-05 beta[5]
   - 1.65104e-05 beta[6] + 1.18258e-05 beta[7]
   + 0.00404764299631211 beta[8] + 0.00108568465074566 beta[9]
   + 4.2331282029572925e-04 beta[10] + 0.000149075 beta[11]
   + 2.65639e-05 beta[12] - 2.25227e-05 beta[13] - 3.73212e-05 beta[14]
   - 3.74202e-05 beta[15] - 0.00562634527884853 beta[16]
   - 8.4197349102366204e-04 beta[17] + 1.4546181249242007e-04 beta[18]
   + 2.8130040921010846e-04 beta[19] + 2.3286258413144148e-04 beta[20]
   + 1.6310927283737058e-04 beta[21] + 0.00010728 beta[22]
   + 6.8544e-05 beta[23] - 1.8018670514763357e-04 beta[24]
   - 0.00183977488318332 beta[25] - 0.00132559969428479 beta[26]
   - 0.0008063 beta[27] - 4.6476048232756649e-04 beta[28]
   - 2.6170054060281671e-04 beta[29] - 1.4536860337904282e-04 beta[30]
   - 7.98152e-05 beta[31] + 0.0119472269999399 beta[32]
   + 0.00571628564913107 beta[33] + 0.00257635309778856 beta[34]
   + 0.00119170540663831 beta[35] + 5.6367488574391974e-04 beta[36]
   + 2.69877210824454e-04 beta[37] + 1.2941840369832083e-04 beta[38]
   + 6.13707e-05 beta[39] - 0.0227989326450029 beta[40]
   - 0.0083331534604697 beta[41] - 0.00314930944608716 beta[42]
   - 0.00123621431124538 beta[43] - 4.9422548615538661e-04 beta[44]
   - 0.000196493 beta[45] - 7.51275e-05 beta[46] - 2.58359e-05 beta[47]
   + 0.0286911619559227 beta[48] + 0.00860879553346905 beta[49]
   + 0.00280283680779994 beta[50] + 9.3639063734595254e-04 beta[51]
   + 0.000304503 beta[52] + 8.75853e-05 beta[53] + 1.54009e-05 beta[54]
   - 5.96228e-06 beta[55] - 0.0260850975822002 beta[56]
   - 0.00673055146926393 beta[57] - 0.00184090712117294 beta[58]
   - 0.00047928 beta[59] - 9.51171e-05 beta[60] + 5.35732e-06 beta[61]
   + 2.41766e-05 beta[62] + 2.16581e-05 beta[63]
   + 0.014956005334561 beta[64] + 0.00371697252776082 beta[65]
   + 8.248875312864834e-04 beta[66] + 1.1660064451194524e-04 beta[67]
   - 3.20058e-05 beta[68] - 4.55497e-05 beta[69] - 3.31031e-05 beta[70]
   - 2.03527e-05 beta[71] - 0.0058655030945709 beta[72]
   - 0.00178307411598577 beta[73] - 3.7947044349645465e-04 beta[74]
   - 3.50713e-05 beta[75] + 2.67211e-05 beta[76] + 2.55501e-05 beta[77]
   + 1.57208e-05 beta[78] + 8.1966e-06 beta[79]
   + 0.00789503748297768 beta[80] + 0.00263854497074084 beta[81]
   + 7.9789117520030414e-04 beta[82] + 0.000243611 beta[83]
   + 7.78946e-05 beta[84] + 2.70341e-05 beta[85] + 1.07169e-05 beta[86]
   + 5.08121e-06 beta[87] - 0.0179285702539989 beta[88]
   - 0.00556946843013863 beta[89] - 0.00171571232838005 beta[90]
   - 5.5200279720373207e-04 beta[91] - 1.8766631006482013e-04 beta[92]
   - 6.76283e-05 beta[93] - 2.59843e-05 beta[94] - 1.07657e-05 beta[95]
   + 0.00042584 beta[96] + 3.370954350188915e-04 beta[97]
   + 9.40382e-05 beta[98] - 1.56108e-05 beta[99] - 5.13441e-05 beta[100]
   - 5.62417e-05 beta[101] - 5.00643e-05 beta[102] - 4.09438e-05 beta[103]
   - 2.6102133013447548e-04 beta[104] - 4.78188e-06 beta[105]
   + 4.9211e-05 beta[106] + 5.41873e-05 beta[107] + 4.67759e-05 beta[108]
   + 3.72736e-05 beta[109] + 2.86355e-05 beta[110] + 2.1547e-05 beta[111]
   - 4.7746425368214163e-04 beta[112] - 2.6023075611027874e-04 beta[113]
   - 1.1367649290758286e-04 beta[114] - 4.60551e-05 beta[115]
   - 1.63892e-05 beta[116] - 3.53913e-06 beta[117] + 1.82075e-06 beta[118]
   + 3.78215e-06 beta[119] + 4.0650576748693656e-04 beta[120]
   + 8.73913e-05 beta[121] + 9.16513e-06 beta[122] - 1.342e-05 beta[123]
   - 1.92122e-05 beta[124] - 1.92213e-05 beta[125] - 1.71985e-05 beta[126]
   - 1.45919e-05 beta[127] + 3.6381714189484722e-04 beta[128]
   + 1.5655129932076219e-04 beta[129] + 7.49625e-05 beta[130]
   + 4.08248e-05 beta[131] + 2.47884e-05 beta[132] + 1.62413e-05 beta[133]
   + 1.11707e-05 beta[134] + 7.91449e-06 beta[135]
   - 1.5386925748228988e-04 beta[136] - 6.11931e-05 beta[137]
   - 3.73717e-05 beta[138] - 2.3521e-05 beta[139] - 1.3983e-05 beta[140]
   - 7.5427e-06 beta[141] - 3.40076e-06 beta[142] - 8.76868e-07 beta[143]
   - 1.4804751675680239e-04 beta[144] - 1.18906e-06 beta[145]
   + 2.06481e-05 beta[146] + 1.78412e-05 beta[147] + 1.15386e-05 beta[148]
   + 6.2775e-06 beta[149] + 2.66032e-06 beta[150] + 4.07621e-07 beta[151]
   - 3.1869287347836839e-04 beta[152] - 0.000115105 beta[153]
   - 4.20391e-05 beta[154] - 1.4236e-05 beta[155] - 3.36777e-06 beta[156]
   + 7.44039e-07 beta[157] + 2.07762e-06 beta[158] + 2.27773e-06 beta[159]
   + 1.4144051705008986e-04 beta[160] + 4.79931e-06 beta[161]
   - 2.15859e-05 beta[162] - 2.36081e-05 beta[163] - 1.96637e-05 beta[164]
   - 1.48459e-05 beta[165] - 1.06306e-05 beta[166] - 7.33999e-06 beta[167]
   + 4.7001670220096076e-04 beta[168] + 0.000193982 beta[169]
   + 9.44325e-05 beta[170] + 5.02402e-05 beta[171] + 2.80852e-05 beta[172]
   + 1.61243e-05 beta[173] + 9.36822e-06 beta[174] + 5.44608e-06 beta[175]
   - 2.3023642341381961e-04 beta[176] - 1.0239152351623065e-04 beta[177]
   - 4.46317e-05 beta[178] - 1.73389e-05 beta[179] - 4.88238e-06 beta[180]
   + 4.0434e-07 beta[181] + 2.31775e-06 beta[182] + 2.71761e-06 beta[183]
   - 0.000147507 beta[184] - 6.68569e-05 beta[185] - 4.22281e-05 beta[186]
   - 2.89503e-05 beta[187] - 2.01753e-05 beta[188] - 1.40823e-05 beta[189]
   - 9.81829e-06 beta[190] - 6.83551e-06 beta[191] - 4.45264e-05 beta[192]
   + 1.5079742041568256e-04 beta[193] - 7.18328e-05 beta[194]
   - 4.8598144195943771e-04 beta[195] - 1.4966559995110984e-04 beta[196]
   + 7.5436182325194778e-04 beta[197] + 0.000791339 beta[198]
   - 4.1053743498803419e-04 beta[199] - 9.3509618371040437e-04 beta[200]
   - 1.1344144892067032e-04 beta[201] + 5.9314568935417422e-04 beta[202]
   + 4.1860852664957204e-04 beta[203] - 3.4094749203052166e-04 beta[204]
   - 7.1385372754889653e-04 beta[205] - 0.00023556 beta[206]
   + 0.000517398 beta[207] + 0.000387992 beta[208] - 0.000114835 beta[209]
   - 3.82008798160971e-04 beta[210] - 4.62909e-05 beta[211]
   + 3.7902489624597191e-04 beta[212] + 0.000308864 beta[213]
   - 1.0032186880629124e-04 beta[214] - 3.0370459083106649e-04 beta[215]
   + 0.00106710198415641 beta[216] + 3.7403932685864394e-04 beta[217]
   - 3.2076529235314233e-04 beta[218] - 0.000413522 beta[219]
   - 2.12783e-05 beta[220] + 2.60620434585912e-04 beta[221]
   + 1.2589531819897498e-04 beta[222] - 1.2994157868161799e-04 beta[223]
   - 0.0012109072880917 beta[224] - 3.2279517737991877e-04 beta[225]
   + 4.9253962578252319e-04 beta[226] + 4.6344410219960677e-04 beta[227]
   - 1.3284751751496682e-04 beta[228] - 0.00043813 beta[229]
   - 1.2979773046623011e-04 beta[230] + 2.7499025058587423e-04 beta[231]
   + 9.93524e-05 beta[232] - 3.59426e-05 beta[233]
   - 1.3541357383784619e-04 beta[234] - 7.54265e-05 beta[235]
   + 7.63035e-05 beta[236] + 0.00015681 beta[237] + 8.94766e-05 beta[238]
   - 5.69885e-05 beta[239] + 9.8210052898478617e-04 beta[240]
   + 3.5237426898769401e-04 beta[241] - 2.4721316804185434e-04 beta[242]
   - 2.9801449742431971e-04 beta[243] + 9.54993e-06 beta[244]
   + 1.4160030535763195e-04 beta[245] - 3.40005e-05 beta[246]
   - 1.5048258279330359e-04 beta[247] - 9.9085362945790234e-04 beta[248]
   - 3.601165019806213e-04 beta[249] + 2.4102939068026269e-04 beta[250]
   + 3.087041680915328e-04 beta[251] + 2.68921e-05 beta[252]
   - 1.205907727406608e-04 beta[253] - 1.02422e-05 beta[254]
   + 8.19127e-05 beta[255] + 5.96333e-05 beta[256]
   + 1.4111547604845395e-04 beta[257] + 1.1556345348717745e-04 beta[258]
   - 6.53219e-05 beta[259] - 1.9288164856332696e-04 beta[260]
   - 1.0042960078043145e-04 beta[261] + 8.64558e-05 beta[262]
   + 1.3665576726279091e-04 beta[263] + 3.9870450447745953e-04 beta[264]
   + 2.91976e-05 beta[265] - 2.2452685671719985e-04 beta[266]
   - 7.79953e-05 beta[267] + 1.86423285666662e-04 beta[268]
   + 0.000171466 beta[269] - 7.64324e-05 beta[270]
   - 1.9741633165953898e-04 beta[271] - 1.44974e-05 beta[272]
   - 4.13311e-05 beta[273] - 3.56213e-05 beta[274] + 4.32536e-06 beta[275]
   + 1.5144e-05 beta[276] - 9.31465e-06 beta[277] - 3.77466e-07 beta[278]
   + 5.12147e-05 beta[279] - 0.000195375 beta[280] + 2.66111e-05 beta[281]
   + 1.7851318390632587e-04 beta[282] + 8.08614e-05 beta[283]
   - 1.0705015918429511e-04 beta[284] - 0.000139994 beta[285]
   - 1.89495e-05 beta[286] + 6.55632e-05 beta[287] - 0.00255564 beta[288]
   + 4.2384e-05 beta[289] - 3.8132332238413613e-04 beta[290]
   + weighted_residual[5] = -0.00207569200072158
 R596: - 0.0310841591967489 beta[0] - 1.4759528427028517e-04 beta[1]
   + 3.4363281068973222e-04 beta[2] + 7.62508e-05 beta[3]
   - 2.40393e-05 beta[4] - 4.3591e-05 beta[5] - 3.94529e-05 beta[6]
   - 3.11184e-05 beta[7] + 0.0118419393409205 beta[8]
   - 8.9840184645106544e-04 beta[9] - 3.7908113760042506e-04 beta[10]
   - 8.84007e-05 beta[11] + 1.13834e-06 beta[12] + 2.14806e-05 beta[13]
   + 2.21548e-05 beta[14] + 1.84837e-05 beta[15]
   + 0.0157751556189874 beta[16] + 0.00382603479714 beta[17]
   + 9.5430352486558588e-04 beta[18] + 0.000288234 beta[19]
   + 1.0180369898111535e-04 beta[20] + 4.06393e-05 beta[21]
   + 1.75774e-05 beta[22] + 7.82447e-06 beta[23]
   - 0.0353987909916904 beta[24] - 0.00611079217489408 beta[25]
   - 0.00151580663872832 beta[26] - 4.9002528342116625e-04 beta[27]
   - 1.9837169950040698e-04 beta[28] - 9.51341e-05 beta[29]
   - 5.12524e-05 beta[30] - 2.98828e-05 beta[31]
   + 0.0312297633620389 beta[32] + 0.00355903341957335 beta[33]
   + 8.4690022593454086e-04 beta[34] + 2.8223844717569098e-04 beta[35]
   + 1.2248760815136865e-04 beta[36] + 6.3699e-05 beta[37]
   + 3.70036e-05 beta[38] + 2.30489e-05 beta[39]
   + 0.0042457056171149 beta[40] + 0.00315663387970603 beta[41]
   + 8.059576959326476e-04 beta[42] + 2.4230579432622015e-04 beta[43]
   + 8.42002e-05 beta[44] + 3.30986e-05 beta[45] + 1.45943e-05 beta[46]
   + 7.15594e-06 beta[47] - 0.0457994176939792 beta[48]
   - 0.00706476671348663 beta[49] - 0.00157384341263837 beta[50]
   - 4.769535487840827e-04 beta[51] - 1.830538693365199e-04 beta[52]
   - 8.49328e-05 beta[53] - 4.57304e-05 beta[54] - 2.74797e-05 beta[55]
   + 0.0414847030280994 beta[56] + 0.00269274197011434 beta[57]
   + 0.000460711 beta[58] + 1.5699072276471117e-04 beta[59]
   + 7.70477e-05 beta[60] + 4.56314e-05 beta[61] + 3.00277e-05 beta[62]
   + 2.10428e-05 beta[63] + 0.0146967694008638 beta[64]
   + 0.00529502642663242 beta[65] + 0.00105229529179619 beta[66]
   + 2.3489955435493994e-04 beta[67] + 5.53933e-05 beta[68]
   + 9.71911e-06 beta[69] - 2.79944e-06 beta[70] - 5.94842e-06 beta[71]
   - 0.0575726987294315 beta[72] - 0.00667622653347047 beta[73]
   - 0.000894061 beta[74] - 1.4587469984062202e-04 beta[75]
   - 2.47046e-05 beta[76] - 5.25596e-07 beta[77] + 4.61852e-06 beta[78]
   + 5.27768e-06 beta[79] + 0.0378489971781488 beta[80]
   - 4.1426331303853932e-04 beta[81] - 7.5774549386846228e-04 beta[82]
   - 3.0622757988404487e-04 beta[83] - 1.2539348302364098e-04 beta[84]
   - 5.86798e-05 beta[85] - 3.13787e-05 beta[86] - 1.86435e-05 beta[87]
   + 0.0126850088394328 beta[88] + 0.00691581389315511 beta[89]
   + 0.00182216218867717 beta[90] + 0.000563797 beta[91]
   + 2.1502046986729133e-04 beta[92] + 9.83588e-05 beta[93]
   + 5.161e-05 beta[94] + 2.99075e-05 beta[95] + 0.000257238 beta[96]
   + 1.5592114467994706e-04 beta[97] + 6.12524e-05 beta[98]
   + 1.60296e-05 beta[99] - 3.60465e-06 beta[100] - 1.14253e-05 beta[101]
   - 1.38963e-05 beta[102] - 1.40075e-05 beta[103]
   + 0.0011169207053201 beta[104] + 0.000417516 beta[105]
   + 2.1201622546550562e-04 beta[106] + 1.2649019318843234e-04 beta[107]
   + 8.42589e-05 beta[108] + 6.01747e-05 beta[109] + 4.50259e-05 beta[110]
   + 3.4855e-05 beta[111] - 5.5694878650522676e-04 beta[112]
   - 1.7384169439989004e-04 beta[113] - 9.2718e-05 beta[114]
   - 5.44165e-05 beta[115] - 3.44546e-05 beta[116] - 2.33373e-05 beta[117]
   - 1.67824e-05 beta[118] - 1.27021e-05 beta[119]
   - 0.00114081614596135 beta[120] - 5.9094516899877174e-04 beta[121]
   - 3.048194791331803e-04 beta[122] - 1.7556365696329835e-04 beta[123]
   - 1.1130223506829045e-04 beta[124] - 7.56159e-05 beta[125]
   - 5.40243e-05 beta[126] - 4.0102e-05 beta[127]
   + 0.00170198669759581 beta[128] + 0.000596407 beta[129]
   + 2.9046559631500004e-04 beta[130] + 1.6582570314917618e-04 beta[131]
   + 1.058344531304323e-04 beta[132] + 7.31554e-05 beta[133]
   + 5.36283e-05 beta[134] + 4.10881e-05 beta[135] - 0.000394335 beta[136]
   + 2.4778747940702478e-04 beta[137] + 1.6740856162720107e-04 beta[138]
   + 9.88599e-05 beta[139] + 5.92743e-05 beta[140] + 3.65736e-05 beta[141]
   + 2.31045e-05 beta[142] + 1.48095e-05 beta[143]
   - 0.00222621105941244 beta[144] - 0.000954052 beta[145]
   - 0.000440342 beta[146] - 2.3196036745216635e-04 beta[147]
   - 1.3669326091466364e-04 beta[148] - 8.79069e-05 beta[149]
   - 6.04586e-05 beta[150] - 4.3774e-05 beta[151]
   + 0.00247621723117931 beta[152] + 4.7277873827597294e-04 beta[153]
   + 1.2625435715407147e-04 beta[154] + 4.50164e-05 beta[155]
   + 2.2551e-05 beta[156] + 1.52847e-05 beta[157] + 1.2374e-05 beta[158]
   + 1.08247e-05 beta[159] + 9.4812150305095767e-04 beta[160]
   + 7.6016531245826091e-04 beta[161] + 0.000377085 beta[162]
   + 1.9472916903842525e-04 beta[163] + 1.0840883284408274e-04 beta[164]
   + 6.48589e-05 beta[165] + 4.12666e-05 beta[166] + 2.75964e-05 beta[167]
   - 0.00305472528787946 beta[168] - 9.8764110732693015e-04 beta[169]
   - 3.6674362259851522e-04 beta[170] - 1.6215816372253428e-04 beta[171]
   - 8.41233e-05 beta[172] - 4.97988e-05 beta[173] - 3.26229e-05 beta[174]
   - 2.30224e-05 beta[175] + 0.00106709267916095 beta[176]
   - 8.33124e-05 beta[177] - 1.1106118062070065e-04 beta[178]
   - 6.56536e-05 beta[179] - 3.51106e-05 beta[180] - 1.86545e-05 beta[181]
   - 1.00519e-05 beta[182] - 5.47466e-06 beta[183]
   + 0.0018520714752698 beta[184] + 9.1699980680706261e-04 beta[185]
   + 3.8754569619297159e-04 beta[186] + 0.00017812 beta[187]
   + 9.10324e-05 beta[188] + 5.14021e-05 beta[189] + 3.16093e-05 beta[190]
   + 2.0844e-05 beta[191] - 9.2850313616396998e-04 beta[192]
   + 8.23597e-06 beta[193] + 3.9217424512048724e-04 beta[194]
   - 0.000193704 beta[195] - 4.8158285467571495e-04 beta[196]
   + 0.000155085 beta[197] + 0.00061825 beta[198] + 7.78654e-05 beta[199]
   - 9.656675095916701e-04 beta[200] - 4.03777e-05 beta[201]
   + 5.6670513921052606e-04 beta[202] + 2.4284111657273661e-04 beta[203]
   - 2.7353814435208745e-04 beta[204] - 2.5142540032221694e-04 beta[205]
   + 4.06692e-05 beta[206] + 9.93458e-05 beta[207]
   + 3.5957573551373162e-04 beta[208] + 3.44615e-05 beta[209]
   - 2.6911741062307442e-04 beta[210] - 2.1711966109072512e-04 beta[211]
   + 1.0200284041418635e-04 beta[212] + 2.5203243998049351e-04 beta[213]
   + 4.20705e-05 beta[214] - 1.8590323478971457e-04 beta[215]
   - 8.97732e-06 beta[216] + 1.91274e-05 beta[217] + 7.83188e-05 beta[218]
   + 8.94076e-05 beta[219] - 6.30833e-06 beta[220] - 9.29227e-05 beta[221]
   - 3.54713e-05 beta[222] + 6.84724e-05 beta[223]
   + 4.4432959614293632e-04 beta[224] - 7.70916e-05 beta[225]
   - 2.6307969021779312e-04 beta[226] + 6.41245e-05 beta[227]
   + 1.803091236213474e-04 beta[228] - 1.2280682748635452e-04 beta[229]
   - 2.0150458974244623e-04 beta[230] + 1.3576143269833395e-04 beta[231]
   + 0.00125396465616282 beta[232] + 8.89973e-05 beta[233]
   - 6.2212226219786966e-04 beta[234] - 1.4159425545482487e-04 beta[235]
   + 0.000462925 beta[236] + 2.3795514711467576e-04 beta[237]
   - 2.73419519356226e-04 beta[238] - 2.3135968595236719e-04 beta[239]
   - 6.9947320402236729e-04 beta[240] - 2.46675e-05 beta[241]
   + 3.7086579875102112e-04 beta[242] + 7.81228e-05 beta[243]
   - 2.6862114210724755e-04 beta[244] - 1.5335588150329921e-04 beta[245]
   + 1.0581432739111463e-04 beta[246] + 1.0465588555680072e-04 beta[247]
   - 0.00127323936838537 beta[248] - 3.36368e-05 beta[249]
   + 6.0699261228768224e-04 beta[250] + 5.20831e-06 beta[251]
   - 4.6310640097397871e-04 beta[252] + 2.51832e-05 beta[253]
   + 4.6525579493170637e-04 beta[254] + 4.90656e-05 beta[255]
   - 3.640735343848013e-04 beta[256] + 2.17934e-05 beta[257]
   + 2.0584731654205775e-04 beta[258] - 2.24621e-06 beta[259]
   - 1.5111952140057185e-04 beta[260] - 7.33822e-07 beta[261]
   + 1.0389872767577471e-04 beta[262] - 5.49944e-05 beta[263]
   + 5.8380176540695223e-04 beta[264] - 2.9674e-05 beta[265]
   - 3.0438687545699636e-04 beta[266] + 3.58423e-05 beta[267]
   + 2.3174145642424485e-04 beta[268] - 6.45739e-05 beta[269]
   - 2.2544328758927003e-04 beta[270] + 9.797e-05 beta[271]
   + 0.00124884393016747 beta[272] + 5.117e-05 beta[273]
   - 6.2832446889508659e-04 beta[274] - 8.83869e-05 beta[275]
   + 0.000472192 beta[276] + 0.000147922 beta[277]
   - 3.3880333380967905e-04 beta[278] - 1.7453122016411945e-04 beta[279]
   + 2.96052e-05 beta[280] + 1.84064e-05 beta[281] + 9.80111e-06 beta[282]
   - 3.39613e-06 beta[283] - 3.118e-05 beta[284] - 4.33083e-05 beta[285]
   - 5.4031e-06 beta[286] + 5.19054e-05 beta[287]
   - 0.0308092341973545 beta[288] + 9.0790576155465829e-04 beta[289]
   - 0.00647266 beta[290] - 1.06863e-05 beta[291] + weighted_residual[6]
   = -0.0304445613613824
 R597: - 0.0314345230395576 beta[0] + 5.4629e-05 beta[1]
   + 0.000903285 beta[2] + 4.3804842846984757e-04 beta[3]
   + 1.8061829504988072e-04 beta[4] + 7.28295e-05 beta[5]
   + 2.95003e-05 beta[6] + 1.1766e-05 beta[7] + 0.00956036891444131 beta[8]
   - 0.0024471052924236 beta[9] - 0.00126596358768275 beta[10]
   - 5.2782880163987518e-04 beta[11] - 2.2109561844143986e-04 beta[12]
   - 9.78426e-05 beta[13] - 4.63317e-05 beta[14] - 2.33848e-05 beta[15]
   + 0.0232474838249477 beta[16] + 0.00661564684588772 beta[17]
   + 0.00194384 beta[18] + 6.6936510939355942e-04 beta[19]
   + 2.6838428564510478e-04 beta[20] + 1.2293233932760458e-04 beta[21]
   + 6.27571e-05 beta[22] + 3.48731e-05 beta[23]
   - 0.0530159115985942 beta[24] - 0.00842044393069137 beta[25]
   - 0.00186744413951696 beta[26] - 0.000528869 beta[27]
   - 1.8909352891414755e-04 beta[28] - 8.26914e-05 beta[29]
   - 4.20504e-05 beta[30] - 2.37375e-05 beta[31]
   + 0.0471284370091124 beta[32] + 0.00317780337119393 beta[33]
   + 1.0308814096518238e-04 beta[34] - 1.2264946439528182e-04 beta[35]
   - 8.82069e-05 beta[36] - 5.17958e-05 beta[37] - 3.05295e-05 beta[38]
   - 1.8866e-05 beta[39] + 0.00465925301964825 beta[40]
   + 0.00582955534484162 beta[41] + 0.00210808697124131 beta[42]
   + 8.3389576962830019e-04 beta[43] + 3.7530347398713682e-04 beta[44]
   + 1.904866185148061e-04 beta[45] + 1.0702639752397202e-04 beta[46]
   + 6.52456e-05 beta[47] - 0.0510058929777717 beta[48]
   - 0.00904176784325161 beta[49] - 0.00249620021393883 beta[50]
   - 9.086428079664176e-04 beta[51] - 4.0239631607073389e-04 beta[52]
   - 2.070211947242483e-04 beta[53] - 1.193577584970566e-04 beta[54]
   - 7.48867e-05 beta[55] + 0.0408712028057075 beta[56]
   + 0.00311424090731577 beta[57] + 0.000761532 beta[58]
   + 0.00031155 beta[59] + 0.000159042 beta[60] + 9.31571e-05 beta[61]
   + 5.99503e-05 beta[62] + 4.11376e-05 beta[63]
   + 0.017641725396001 beta[64] + 0.00536683261066355 beta[65]
   + 0.00117343043875514 beta[66] + 3.234757945672521e-04 beta[67]
   + 1.0698663240946057e-04 beta[68] + 3.84623e-05 beta[69]
   + 1.34522e-05 beta[70] + 3.57065e-06 beta[71]
   - 0.0670794776519063 beta[72] - 0.00811808494045595 beta[73]
   - 0.00153955497303529 beta[74] - 4.6284417857885723e-04 beta[75]
   - 1.8675881403178531e-04 beta[76] - 8.86972e-05 beta[77]
   - 4.6725e-05 beta[78] - 2.65617e-05 beta[79]
   + 0.0547961071807683 beta[80] + 0.00307292812476713 beta[81]
   + 3.5296626135461137e-04 beta[82] + 1.3985981189395689e-04 beta[83]
   + 8.4665e-05 beta[84] + 5.2981e-05 beta[85] + 3.38141e-05 beta[86]
   + 2.22827e-05 beta[87] - 0.00128689214702832 beta[88]
   + 0.00365707609360201 beta[89] + 9.3924689277723433e-04 beta[90]
   + 2.3877028158896855e-04 beta[91] + 6.21011e-05 beta[92]
   + 1.38989e-05 beta[93] - 6.32563e-08 beta[94] - 3.95537e-06 beta[95]
   - 3.2512669147933187e-04 beta[96] - 8.49538e-07 beta[97]
   - 1.37605e-05 beta[98] - 2.58311e-05 beta[99] - 2.84269e-05 beta[100]
   - 2.67507e-05 beta[101] - 2.38068e-05 beta[102] - 2.07784e-05 beta[103]
   + 8.4727011499974888e-04 beta[104] + 0.000425873 beta[105]
   + 2.0640148181719169e-04 beta[106] + 1.064311648309448e-04 beta[107]
   + 6.10089e-05 beta[108] + 3.87088e-05 beta[109] + 2.67189e-05 beta[110]
   + 1.96852e-05 beta[111] - 0.00100942740660271 beta[112]
   - 8.88592e-05 beta[113] + 2.64278e-05 beta[114] + 3.81335e-05 beta[115]
   + 3.28565e-05 beta[116] + 2.60082e-05 beta[117] + 2.03159e-05 beta[118]
   + 1.59749e-05 beta[119] - 0.00147506637435856 beta[120]
   - 8.2459554745393203e-04 beta[121] - 0.000431212 beta[122]
   - 0.000242507 beta[123] - 1.4910338234692914e-04 beta[124]
   - 9.90498e-05 beta[125] - 7.00016e-05 beta[126] - 5.1922e-05 beta[127]
   + 0.00269574637331887 beta[128] + 6.3253842325285375e-04 beta[129]
   + 2.2481956533877624e-04 beta[130] + 1.060135135500921e-04 beta[131]
   + 6.14938e-05 beta[132] + 4.0992e-05 beta[133] + 2.99322e-05 beta[134]
   + 2.32204e-05 beta[135] + 4.1124520242066272e-04 beta[136]
   + 5.9979020754754035e-04 beta[137] + 3.5325331548822174e-04 beta[138]
   + 2.0695056692492957e-04 beta[139] + 0.000128161 beta[140]
   + 8.41011e-05 beta[141] + 5.80099e-05 beta[142] + 4.16804e-05 beta[143]
   - 0.00278565952831837 beta[144] - 0.00101938 beta[145]
   - 4.5938628784802129e-04 beta[146] - 2.4839380457246417e-04 beta[147]
   - 1.5331632492999981e-04 beta[148] - 1.0367930977052907e-04 beta[149]
   - 7.47629e-05 beta[150] - 5.64926e-05 beta[151] + 0.00189879 beta[152]
   + 0.000255952 beta[153] + 4.84202e-05 beta[154] + 1.60994e-05 beta[155]
   + 1.15371e-05 beta[156] + 1.11931e-05 beta[157] + 1.11333e-05 beta[158]
   + 1.08349e-05 beta[159] + 0.000563608 beta[160]
   + 6.0238980535891275e-04 beta[161] + 0.0003142 beta[162]
   + 1.7033074148949307e-04 beta[163] + 0.000100177 beta[164]
   + 6.34428e-05 beta[165] + 4.26534e-05 beta[166] + 3.00506e-05 beta[167]
   - 0.00276555885295929 beta[168] - 8.0597783575270243e-04 beta[169]
   - 3.1138215842551421e-04 beta[170] - 1.5162081743747726e-04 beta[171]
   - 8.7242e-05 beta[172] - 5.63514e-05 beta[173] - 3.94497e-05 beta[174]
   - 2.92489e-05 beta[175] + 0.0016365603317781 beta[176]
   + 1.5178732732015342e-04 beta[177] + 9.96536e-06 beta[178]
   + 2.5062e-06 beta[179] + 6.04888e-06 beta[180] + 7.83609e-06 beta[181]
   + 8.00336e-06 beta[182] + 7.4517e-06 beta[183]
   + 0.00160949373673985 beta[184] + 6.6273647138359202e-04 beta[185]
   + 2.5930678219420741e-04 beta[186] + 0.000112043 beta[187]
   + 5.30086e-05 beta[188] + 2.70292e-05 beta[189] + 1.46444e-05 beta[190]
   + 8.33206e-06 beta[191] - 0.0013404822764905 beta[192]
   + 1.0480619659841425e-04 beta[193] + 8.2155084897799684e-04 beta[194]
   - 4.33463e-05 beta[195] - 8.2349621607127313e-04 beta[196]
   - 2.2228462978319215e-04 beta[197] + 0.000683195 beta[198]
   + 4.4392448073208565e-04 beta[199] - 7.7470188005640561e-04 beta[200]
   - 1.9672961176496064e-04 beta[201] + 2.7538061679971957e-04 beta[202]
   + 2.3985062362679729e-04 beta[203] - 1.00344e-05 beta[204]
   - 1.0076838809406079e-04 beta[205] - 6.00977e-05 beta[206]
   - 3.30625e-05 beta[207] + 0.000620553 beta[208]
   + 1.7655288538015351e-04 beta[209] - 2.7654046013821261e-04 beta[210]
   - 2.9299334649073662e-04 beta[211] + 6.85321e-05 beta[212]
   + 0.000280732 beta[213] + 5.36799e-05 beta[214]
   - 2.3511673191655975e-04 beta[215] + 3.4947264835202569e-04 beta[216]
   + 1.04781e-05 beta[217] - 0.000120456 beta[218] + 7.55861e-05 beta[219]
   + 1.2937512883454347e-04 beta[220] - 0.00010236 beta[221]
   - 1.7275461744342715e-04 beta[222] + 8.94888e-05 beta[223]
   + 0.000259605 beta[224] - 1.5120333484516406e-04 beta[225]
   - 2.3041658111012136e-04 beta[226] + 1.1992620646990628e-04 beta[227]
   + 2.1083612105291828e-04 beta[228] - 0.000103853 beta[229]
   - 1.9036579020325088e-04 beta[230] + 1.0467187387420355e-04 beta[231]
   + 3.2159374378618283e-04 beta[232] + 1.2926776121475396e-04 beta[233]
   - 7.40203e-05 beta[234] - 1.1429057954608817e-04 beta[235]
   + 2.68029e-06 beta[236] + 0.000107955 beta[237] + 5.88857e-05 beta[238]
   - 8.346e-05 beta[239] - 5.1526310972725947e-04 beta[240]
   - 6.2587e-05 beta[241] + 2.1187436560033326e-04 beta[242]
   + 5.85939e-05 beta[243] - 0.000122325 beta[244] - 6.72009e-05 beta[245]
   + 2.36673e-05 beta[246] + 2.21367e-05 beta[247] - 0.000562232 beta[248]
   + 4.2315e-05 beta[249] + 0.000291205 beta[250] - 6.63252e-05 beta[251]
   - 2.3922315914543028e-04 beta[252] + 9.99685e-05 beta[253]
   + 0.000279105 beta[254] - 5.98473e-05 beta[255]
   - 5.5492022570400484e-04 beta[256] - 1.3325e-05 beta[257]
   + 2.973228381604855e-04 beta[258] + 4.56478e-05 beta[259]
   - 2.2933540576585635e-04 beta[260] - 8.78508e-05 beta[261]
   + 1.4825573942330833e-04 beta[262] + 6.83682e-05 beta[263]
   + 3.9894369480726545e-04 beta[264] - 7.8673e-05 beta[265]
   - 2.4290554885823593e-04 beta[266] + 8.62261e-05 beta[267]
   + 0.000226212 beta[268] - 7.37442e-05 beta[269]
   - 2.1439359143701056e-04 beta[270] + 8.34e-05 beta[271]
   + 0.00125261083982123 beta[272] + 0.000115365 beta[273]
   - 5.864818122597894e-04 beta[274] - 1.5137666928483087e-04 beta[275]
   + 3.9081864230113505e-04 beta[276] + 1.6996716374339488e-04 beta[277]
   - 2.6436113740932894e-04 beta[278] - 1.7619148069995903e-04 beta[279]
   + 2.717602771226515e-04 beta[280] - 3.36705e-06 beta[281]
   - 1.4143469669152892e-04 beta[282] + 3.19949e-06 beta[283]
   + 1.1118285891559535e-04 beta[284] - 1.52661e-05 beta[285]
   - 1.24329611094634e-04 beta[286] + 9.10787e-06 beta[287]
   - 0.0309571697714706 beta[288] + 5.4476116659117732e-04 beta[289]
   - 0.00399619633605032 beta[290] - 7.7986e-06 beta[291]
   + weighted_residual[7] = -0.0306944805753814
 R598: - 0.00517212350451533 beta[0] - 0.00526148563741739 beta[1]
   - 0.00195011415239047 beta[2] - 7.6172673528113622e-04 beta[3]
   - 3.4628379265058169e-04 beta[4] - 0.000181741 beta[5]
   - 1.0632063231752314e-04 beta[6] - 6.70353e-05 beta[7]
   + 0.034375826045571 beta[8] + 0.00376024862697671 beta[9]
   + 0.000685274 beta[10] + 0.000219409 beta[11]
   + 1.1299735228304594e-04 beta[12] + 7.13919e-05 beta[13]
   + 4.82841e-05 beta[14] + 3.36459e-05 beta[15]
   - 0.029644911405363 beta[16] + 0.00193538873981944 beta[17]
   + 0.00104665556557572 beta[18] + 3.2867755602176193e-04 beta[19]
   + 9.06665e-05 beta[20] + 1.85882e-05 beta[21] - 2.24062e-06 beta[22]
   - 7.41235e-06 beta[23] - 0.00709377785572754 beta[24]
   - 0.00481371790645555 beta[25] - 0.00117550657772278 beta[26]
   - 2.4491124366031773e-04 beta[27] - 3.46544e-05 beta[28]
   + 1.01363e-05 beta[29] + 1.69411e-05 beta[30] + 1.54336e-05 beta[31]
   + 0.0143211402259782 beta[32] - 0.00204254851275627 beta[33]
   - 0.000933433 beta[34] - 4.1542836137188469e-04 beta[35]
   - 2.0257737327292346e-04 beta[36] - 1.0879744815480266e-04 beta[37]
   - 6.38627e-05 beta[38] - 4.04377e-05 beta[39]
   + 0.0135866718211917 beta[40] + 0.00966104517101035 beta[41]
   + 0.00265068207032879 beta[42] + 8.500781350516374e-04 beta[43]
   + 3.3477964314922387e-04 beta[44] + 1.5671765342770329e-04 beta[45]
   + 8.39872e-05 beta[46] + 4.99182e-05 beta[47]
   - 0.0270031696722945 beta[48] - 0.00623839880528432 beta[49]
   - 0.00168612847316745 beta[50] - 5.5834164859621988e-04 beta[51]
   - 2.2801062107434184e-04 beta[52] - 1.0970341127902932e-04 beta[53]
   - 5.98353e-05 beta[54] - 3.59175e-05 beta[55]
   + 0.00802113705392431 beta[56] - 0.00397358968855858 beta[57]
   - 6.4135522923874639e-04 beta[58] - 5.57915e-05 beta[59]
   + 2.42578e-05 beta[60] + 2.67754e-05 beta[61] + 2.02347e-05 beta[62]
   + 1.45367e-05 beta[63] + 0.0200347784062229 beta[64]
   + 0.00868027274927127 beta[65] + 0.00168675140497762 beta[66]
   + 3.5142443385310457e-04 beta[67] + 8.51971e-05 beta[68]
   + 2.24288e-05 beta[69] + 4.97107e-06 beta[70] - 3.31528e-07 beta[71]
   - 0.0368282302471547 beta[72] - 0.00446495266613113 beta[73]
   - 7.9537277623170448e-04 beta[74] - 1.8173015699992923e-04 beta[75]
   - 5.70468e-05 beta[76] - 2.27183e-05 beta[77] - 1.03627e-05 beta[78]
   - 5.12163e-06 beta[79] + 0.031781561828345 beta[80]
   - 0.00274240897350858 beta[81] - 7.982244273029228e-04 beta[82]
   - 0.000178571 beta[83] - 3.47081e-05 beta[84] - 1.67129e-06 beta[85]
   + 5.3583e-06 beta[86] + 6.07805e-06 beta[87]
   - 0.00535744565037056 beta[88] + 0.00624761137179145 beta[89]
   + 0.00163039730070994 beta[90] + 3.9363561178671578e-04 beta[91]
   + 9.67747e-05 beta[92] + 2.04546e-05 beta[93] - 3.9083e-07 beta[94]
   - 5.83656e-06 beta[95] + 0.00411970932501557 beta[96]
   + 4.0789077745292279e-04 beta[97] - 1.969077640384039e-04 beta[98]
   - 0.000243202 beta[99] - 1.9657634355084363e-04 beta[100]
   - 1.4693711726998309e-04 beta[101] - 1.0901865828457155e-04 beta[102]
   - 8.20455e-05 beta[103] + 0.00178797747349269 beta[104]
   + 7.6938821791120316e-04 beta[105] + 3.0777481135686041e-04 beta[106]
   + 1.2818761557429245e-04 beta[107] + 5.80371e-05 beta[108]
   + 2.86791e-05 beta[109] + 1.53096e-05 beta[110] + 8.68507e-06 beta[111]
   - 0.00207517694734112 beta[112] - 7.3711e-05 beta[113]
   + 1.6182274876557181e-04 beta[114] + 1.5437882311420114e-04 beta[115]
   + 1.171783142959343e-04 beta[116] + 8.56952e-05 beta[117]
   + 6.32743e-05 beta[118] + 4.7816e-05 beta[119]
   - 0.00226013241701464 beta[120] - 0.00127747014087192 beta[121]
   - 5.6132030634114681e-04 beta[122] - 2.5791971674232934e-04 beta[123]
   - 1.3027741919058344e-04 beta[124] - 7.25241e-05 beta[125]
   - 4.40154e-05 beta[126] - 2.87078e-05 beta[127]
   + 0.0019826407758553 beta[128] + 3.1177985106864366e-04 beta[129]
   + 2.03287e-05 beta[130] - 3.78581e-05 beta[131] - 4.25064e-05 beta[132]
   - 3.64389e-05 beta[133] - 2.96744e-05 beta[134] - 2.4133e-05 beta[135]
   + 0.00141379807721878 beta[136] + 0.00128859100821724 beta[137]
   + 6.0373127165930446e-04 beta[138] + 2.9270289219240968e-04 beta[139]
   + 1.5617867743876723e-04 beta[140] + 9.19684e-05 beta[141]
   + 5.90718e-05 beta[142] + 4.0758e-05 beta[143]
   - 0.00200870684743979 beta[144] - 8.6670974991747817e-04 beta[145]
   - 3.4648448186306381e-04 beta[146] - 0.000150868 beta[147]
   - 7.42824e-05 beta[148] - 4.0819e-05 beta[149] - 2.4393e-05 beta[150]
   - 1.54966e-05 beta[151] + 5.770795871646719e-04 beta[152]
   - 0.0004539 beta[153] - 2.2673234358884761e-04 beta[154]
   - 1.0542812678718114e-04 beta[155] - 5.15752e-05 beta[156]
   - 2.72294e-05 beta[157] - 1.56545e-05 beta[158] - 9.81246e-06 beta[159]
   + 6.7781434444837987e-04 beta[160] + 0.000842178 beta[161]
   + 3.6704921491908799e-04 beta[162] + 0.000163635 beta[163]
   + 8.02879e-05 beta[164] + 4.307e-05 beta[165] + 2.47002e-05 beta[166]
   + 1.48236e-05 beta[167] - 0.0015826057363206 beta[168]
   - 4.276073942243592e-04 beta[169] - 1.7454172922585397e-04 beta[170]
   - 8.1258e-05 beta[171] - 4.31875e-05 beta[172] - 2.52872e-05 beta[173]
   - 1.56836e-05 beta[174] - 1.00154e-05 beta[175]
   + 0.00112642043878197 beta[176] - 1.8768812465472611e-04 beta[177]
   - 7.90385e-05 beta[178] - 2.40691e-05 beta[179] - 5.11067e-06 beta[180]
   + 1.22753e-06 beta[181] + 3.28476e-06 beta[182] + 3.82096e-06 beta[183]
   + 8.8399723370868411e-04 beta[184] + 6.2281529601070692e-04 beta[185]
   + 2.5671226538507967e-04 beta[186] + 1.0536887440463001e-04 beta[187]
   + 4.59092e-05 beta[188] + 2.07963e-05 beta[189] + 9.17648e-06 beta[190]
   + 3.36565e-06 beta[191] + 0.00140172700340351 beta[192]
   - 7.7918134395466813e-04 beta[193] - 0.00167185837623954 beta[194]
   + 0.000118256 beta[195] + 0.00175175022835891 beta[196]
   + 0.00073812 beta[197] - 0.00122048776542296 beta[198]
   - 0.00113044 beta[199] - 0.00172273874803701 beta[200]
   + 5.3477249642041485e-04 beta[201] + 0.00162576033382546 beta[202]
   + 7.39356e-05 beta[203] - 0.00152182842207465 beta[204]
   - 0.000761685 beta[205] + 9.625344298956716e-04 beta[206]
   + 0.00100899682205143 beta[207] - 0.00137141299753571 beta[208]
   - 0.000366066 beta[209] + 2.1301060896342891e-04 beta[210]
   - 4.209e-05 beta[211] - 8.19321e-05 beta[212] + 0.0003902 beta[213]
   + 3.5562374091445051e-04 beta[214] - 3.8632126791759497e-04 beta[215]
   + 0.00151545855138147 beta[216] + 1.9152885197375999e-04 beta[217]
   - 5.6635872266732679e-04 beta[218] - 4.54591e-06 beta[219]
   + 5.0981078839281953e-04 beta[220] - 8.41698e-06 beta[221]
   - 5.9296460929658863e-04 beta[222] - 1.8716989353682775e-04 beta[223]
   + 0.00204245073554819 beta[224] + 2.11744e-05 beta[225]
   - 0.000998719 beta[226] - 6.21329e-05 beta[227] + 0.000582375 beta[228]
   - 1.2576437316498941e-04 beta[229] - 4.6057028473517938e-04 beta[230]
   + 3.6061774652227442e-04 beta[231] + 0.00147285116277726 beta[232]
   + 7.01473e-06 beta[233] - 0.000853303 beta[234]
   - 1.2457024239637395e-04 beta[235] + 7.7394936960084712e-04 beta[236]
   + 0.000418438 beta[237] - 5.2149238213565388e-04 beta[238]
   - 6.0091483610423817e-04 beta[239] - 0.00375926852388283 beta[240]
   - 5.18208e-05 beta[241] + 0.00199726557823705 beta[242]
   + 2.2981313793041171e-04 beta[243] - 0.00154445620221704 beta[244]
   - 4.82071404789951e-04 beta[245] + 0.00108124306403152 beta[246]
   + 5.2387864303648482e-04 beta[247] - 0.00352359397015176 beta[248]
   - 2.1245872251354081e-04 beta[249] + 0.00165321961432721 beta[250]
   + 0.000187169 beta[251] - 0.00121665702000656 beta[252]
   - 1.3883036791610242e-04 beta[253] + 0.00114719162833902 beta[254]
   + 2.8881483598585745e-04 beta[255] + 0.00385099061319603 beta[256]
   + 3.3096768283899318e-04 beta[257] - 0.00182370574800894 beta[258]
   - 3.9895316752716246e-04 beta[259] + 0.00132477906093142 beta[260]
   + 0.000468472 beta[261] - 0.00111015515123244 beta[262]
   - 6.5991874657007465e-04 beta[263] + 0.00333996413882165 beta[264]
   - 2.26487e-05 beta[265] - 0.00173131446190506 beta[266]
   - 3.077e-05 beta[267] + 0.00131105568384661 beta[268]
   + 3.56832e-05 beta[269] - 0.00111305089005042 beta[270]
   + 1.73011e-05 beta[271] - 0.00188206737039533 beta[272]
   - 1.37823443843225e-04 beta[273] + 9.5536935654656015e-04 beta[274]
   + 2.4185570173778346e-04 beta[275] - 6.8285141591963006e-04 beta[276]
   - 0.000278101 beta[277] + 0.000563734 beta[278]
   + 3.0380526067982591e-04 beta[279] - 0.00306971172796185 beta[280]
   - 6.87719e-05 beta[281] + 0.00153220427585695 beta[282]
   + 8.97877e-05 beta[283] - 0.00117627094669902 beta[284]
   - 0.000148409 beta[285] + 9.6212922932808933e-04 beta[286]
   + 1.7516456881991641e-04 beta[287] - 0.003857152862425 beta[288]
   + 7.9803343098507615e-04 beta[289] - 0.00718182458841103 beta[290]
   + 8.53609e-07 beta[291] + weighted_residual[8] = -0.00817197788843361
 R599: - 0.0457860663424818 beta[0] + 0.00584186866032518 beta[1]
   + 0.00274425051147978 beta[2] + 0.000879109 beta[3]
   + 2.6933635768926494e-04 beta[4] + 8.97972e-05 beta[5]
   + 3.7181e-05 beta[6] + 2.03423e-05 beta[7] - 0.0480656257569154 beta[8]
   - 0.0179574148328873 beta[9] - 0.00526104017935402 beta[10]
   - 0.00149598709086999 beta[11] - 4.4406971474882751e-04 beta[12]
   - 0.000144755 beta[13] - 5.44466e-05 beta[14] - 2.44789e-05 beta[15]
   + 0.1910217785200795 beta[16] + 0.0289369277322996 beta[17]
   + 0.00586853063138165 beta[18] + 0.00134581193241082 beta[19]
   + 3.3566754493443226e-04 beta[20] + 8.67741e-05 beta[21]
   + 2.03091e-05 beta[22] + 1.78877e-06 beta[23]
   - 0.1853920863604459 beta[24] - 0.0190975525271385 beta[25]
   - 0.00186402737663092 beta[26] + 6.52768e-05 beta[27]
   + 1.8605874238698233e-04 beta[28] + 0.000130346 beta[29]
   + 8.35872e-05 beta[30] + 5.47146e-05 beta[31]
   + 0.042980615659273 beta[32] - 0.00604102221655265 beta[33]
   - 0.00383518803699557 beta[34] - 0.00163806535252159 beta[35]
   - 7.1525520814728612e-04 beta[36] - 3.4319520059408455e-04 beta[37]
   - 1.8238887427729958e-04 beta[38] - 1.0588625195958611e-04 beta[39]
   + 0.0701672505895141 beta[40] + 0.0230771539711048 beta[41]
   + 0.0067661735390362 beta[42] + 0.00223406106505761 beta[43]
   + 8.6251874780516181e-04 beta[44] + 3.8573977117746299e-04 beta[45]
   + 0.000194701 beta[46] + 1.0798166987045303e-04 beta[47]
   - 0.1415404605053143 beta[48] - 0.0259886770061505 beta[49]
   - 0.00614705955846689 beta[50] - 0.00178033693821264 beta[51]
   - 6.1764039089263806e-04 beta[52] - 2.507594117405597e-04 beta[53]
   - 1.1555973496614871e-04 beta[54] - 5.8676e-05 beta[55]
   + 0.1397426193394725 beta[56] + 0.018816999220886 beta[57]
   + 0.00357188640750125 beta[58] + 0.000813169 beta[59]
   + 2.0090061856237277e-04 beta[60] + 4.71201e-05 beta[61]
   + 5.8349e-06 beta[62] - 5.0177e-06 beta[63]
   - 0.0305165756576131 beta[64] - 0.00299406088386785 beta[65]
   - 3.59802e-05 beta[66] + 0.000268695 beta[67] + 0.000200589 beta[68]
   + 0.000123349 beta[69] + 7.43888e-05 beta[70] + 4.59287e-05 beta[71]
   - 0.0818657267887773 beta[72] - 0.013219413469807 beta[73]
   - 0.00336717303520365 beta[74] - 0.00118064882065996 beta[75]
   - 4.8147786496887795e-04 beta[76] - 0.00021619 beta[77]
   - 1.0508487701275666e-04 beta[78] - 5.47347e-05 beta[79]
   + 0.1213016826358797 beta[80] + 0.0196155681199946 beta[81]
   + 0.0047932390730578 beta[82] + 0.00149296299601657 beta[83]
   + 5.3578182513622935e-04 beta[84] + 2.1299838598871286e-04 beta[85]
   + 9.18995e-05 beta[86] + 4.23427e-05 beta[87]
   - 0.0850580299495518 beta[88] - 0.0135696643562423 beta[89]
   - 0.00333231775667721 beta[90] - 0.000984908 beta[91]
   - 3.2769275405213121e-04 beta[92] - 1.2103160325406591e-04 beta[93]
   - 4.93546e-05 beta[94] - 2.20827e-05 beta[95]
   + 0.00266829498304423 beta[96] - 0.00133321672974669 beta[97]
   - 0.00117024863963178 beta[98] - 7.1368080651904844e-04 beta[99]
   - 4.1335266307397726e-04 beta[100] - 2.4315577457783471e-04 beta[101]
   - 1.4807365377405397e-04 beta[102] - 9.36476e-05 beta[103]
   + 0.00976130495445724 beta[104] + 0.00128475623831658 beta[105]
   + 6.88197e-05 beta[106] - 8.09843e-05 beta[107] - 6.77564e-05 beta[108]
   - 4.25624e-05 beta[109] - 2.59787e-05 beta[110] - 1.67993e-05 beta[111]
   + 0.00521468328588531 beta[112] + 0.00179941219603871 beta[113]
   + 9.1970840132668118e-04 beta[114] + 5.0312419106325027e-04 beta[115]
   + 2.8745774452163198e-04 beta[116] + 1.7243310697855307e-04 beta[117]
   + 1.0891424749750561e-04 beta[118] + 7.23443e-05 beta[119]
   - 0.00818689086980372 beta[120] - 0.00202472542230425 beta[121]
   - 5.5750230902961828e-04 beta[122] - 1.8318128149505343e-04 beta[123]
   - 7.90476e-05 beta[124] - 4.46973e-05 beta[125] - 2.96574e-05 beta[126]
   - 2.09429e-05 beta[127] - 0.00431327121318474 beta[128]
   - 0.00100678546628249 beta[129] - 0.000431316 beta[130]
   - 2.3584176292072687e-04 beta[131] - 1.4281660024702839e-04 beta[132]
   - 9.222e-05 beta[133] - 6.2923e-05 beta[134] - 4.51737e-05 beta[135]
   - 1.927525012867508e-04 beta[136] + 0.00104660861083598 beta[137]
   + 5.5604919882281994e-04 beta[138] + 2.8910682745310963e-04 beta[139]
   + 1.6937713278452189e-04 beta[140] + 1.111265853429672e-04 beta[141]
   + 7.87231e-05 beta[142] + 5.84922e-05 beta[143]
   - 6.9164945435009337e-04 beta[144] - 0.000273491 beta[145]
   - 0.000175065 beta[146] - 0.000110756 beta[147] - 7.11075e-05 beta[148]
   - 4.74709e-05 beta[149] - 3.30016e-05 beta[150] - 2.36988e-05 beta[151]
   + 0.00537510359954768 beta[152] + 8.285475765553936e-04 beta[153]
   + 0.000143429 beta[154] + 2.33471e-05 beta[155] - 3.95294e-06 beta[156]
   - 1.21469e-05 beta[157] - 1.46605e-05 beta[158] - 1.48878e-05 beta[159]
   + 0.000416605 beta[160] - 2.1356040283583238e-04 beta[161]
   - 9.4374e-05 beta[162] - 1.83342e-05 beta[163] + 1.17788e-05 beta[164]
   + 2.15581e-05 beta[165] + 2.33436e-05 beta[166] + 2.21426e-05 beta[167]
   - 0.00146486068531481 beta[168] - 6.0736118558094943e-04 beta[169]
   - 2.1178540951762002e-04 beta[170] - 9.65461e-05 beta[171]
   - 5.48067e-05 beta[172] - 3.46384e-05 beta[173] - 2.29546e-05 beta[174]
   - 1.56087e-05 beta[175] + 0.0016297485600751 beta[176]
   + 8.0844972997281509e-04 beta[177] + 0.000421859 beta[178]
   + 2.2047814297995104e-04 beta[179] + 1.1654054152586265e-04 beta[180]
   + 6.21811e-05 beta[181] + 3.29513e-05 beta[182] + 1.67643e-05 beta[183]
   - 0.00369098094069621 beta[184] - 8.5301755302923988e-04 beta[185]
   - 3.0195541735864435e-04 beta[186] - 1.3340785204438903e-04 beta[187]
   - 6.4824e-05 beta[188] - 3.26891e-05 beta[189] - 1.64133e-05 beta[190]
   - 7.73512e-06 beta[191] - 1.9303561188292823e-04 beta[192]
   - 7.5558637298927124e-04 beta[193] - 7.1790743667129477e-04 beta[194]
   + 2.7279913009301611e-04 beta[195] + 0.00101114633367483 beta[196]
   + 4.9773450727443004e-04 beta[197] - 5.2520968908208589e-04 beta[198]
   - 6.9880329403615622e-04 beta[199] - 0.0030045531231673 beta[200]
   + 8.0572085180107076e-04 beta[201] + 0.00246981743302815 beta[202]
   - 0.000275111 beta[203] - 0.00259989292106707 beta[204]
   - 7.3039952313097686e-04 beta[205] + 0.00209842877787239 beta[206]
   + 0.00137579518713675 beta[207] + 0.00507105576126637 beta[208]
   - 0.000827237 beta[209] - 0.00351490946136407 beta[210]
   + 3.6944419860105609e-04 beta[211] + 0.00354036585632345 beta[212]
   + 6.7739327851206756e-04 beta[213] - 0.00313418422729604 beta[214]
   - 0.0016128929789523 beta[215] + 0.00130176406709435 beta[216]
   + 0.000799205 beta[217] - 2.11781e-05 beta[218]
   - 6.82628380881794e-04 beta[219] - 0.000627288 beta[220]
   + 1.4612317905421014e-04 beta[221] + 7.8385038102783753e-04 beta[222]
   + 4.1852633732245812e-04 beta[223] - 0.00551829525525435 beta[224]
   - 4.2648863221376272e-04 beta[225] + 0.00275522234958661 beta[226]
   + 0.00067934 beta[227] - 0.00203533123885506 beta[228]
   - 9.4326049462091293e-04 beta[229] + 0.00155504989192819 beta[230]
   + 0.00117885514932314 beta[231] + 0.00366640764441775 beta[232]
   - 2.9794812693856434e-04 beta[233] - 0.00241458278644082 beta[234]
   - 6.84952e-05 beta[235] + 0.0024021838118626 beta[236]
   + 0.000882836 beta[237] - 0.00209879543420185 beta[238]
   - 0.00173174700817887 beta[239] - 0.00162573567727146 beta[240]
   + 0.000858037 beta[241] + 0.00162949708214217 beta[242]
   - 6.1555273494038546e-04 beta[243] - 0.00208452809864289 beta[244]
   - 0.000229792 beta[245] + 0.00203327096476629 beta[246]
   + 0.00113668145876878 beta[247] - 0.00197367333714636 beta[248]
   - 0.000977633 beta[249] + 3.6253687584268559e-04 beta[250]
   + 0.00098651 beta[251] + 3.9362125501661013e-04 beta[252]
   - 5.7877664598634745e-04 beta[253] - 6.5882730948591689e-04 beta[254]
   + 1.4698446173035329e-04 beta[255] + 0.00490125015813254 beta[256]
   + 0.000687542 beta[257] - 0.00226760011088551 beta[258]
   - 9.1707463518215875e-04 beta[259] + 0.00152345382393587 beta[260]
   + 0.00109468382030424 beta[261] - 0.00108157208220873 beta[262]
   - 0.00131825548492118 beta[263] - 0.00498386212974591 beta[264]
   - 1.0270710536504376e-04 beta[265] + 0.0027291972057365 beta[266]
   + 3.5128558769134726e-04 beta[267] - 0.00235583262040752 beta[268]
   - 8.7430670422871662e-04 beta[269] + 0.00201965043054735 beta[270]
   + 0.00150491889574385 beta[271] + 0.00127059281570502 beta[272]
   - 0.000515276 beta[273] - 0.00108072581521345 beta[274]
   + 4.5551545960408356e-04 beta[275] + 0.00137753503501839 beta[276]
   + 2.12361e-05 beta[277] - 0.00142590041918035 beta[278]
   - 6.2922778515969073e-04 beta[279] + 0.00341524922116206 beta[280]
   + 8.2092434300859549e-04 beta[281] - 0.0013083426201346 beta[282]
   - 9.8259455004523488e-04 beta[283] + 4.5849773435336521e-04 beta[284]
   + 7.9681918503103546e-04 beta[285] - 2.71204e-05 beta[286]
   - 5.081435182156585e-04 beta[287] - 0.0412950643056124 beta[288]
   + 0.00155259011681048 beta[289] + 0.0113659161072361 beta[290]
   + 5.36176e-07 beta[291] + weighted_residual[9] = -0.0323708096285408
 R600: 0.00151385599922702 beta[0] - 0.00293835983174845 beta[1]
   - 0.00187052733444781 beta[2] - 7.7161080121580902e-04 beta[3]
   - 2.9365821569842692e-04 beta[4] - 1.0409328007317518e-04 beta[5]
   - 3.04307e-05 beta[6] - 2.58975e-06 beta[7]
   - 0.00636970468916161 beta[8] - 0.00538309300690028 beta[9]
   - 0.00141913757091573 beta[10] - 2.4928136117403676e-04 beta[11]
   - 1.04274e-05 beta[12] + 1.76799e-05 beta[13] + 1.1034e-05 beta[14]
   + 3.66072e-06 beta[15] + 0.1086187378081004 beta[16]
   + 0.01540184552282 beta[17] + 0.00307311457200315 beta[18]
   + 6.0276739926711832e-04 beta[19] + 8.91819e-05 beta[20]
   - 1.08951e-05 beta[21] - 2.37669e-05 beta[22] - 2.00119e-05 beta[23]
   - 0.1162144441668172 beta[24] - 0.00857946541460861 beta[25]
   - 1.3579378542249537e-04 beta[26] + 3.735156623781765e-04 beta[27]
   + 0.000244928 beta[28] + 1.4169722897870092e-04 beta[29]
   + 8.4829e-05 beta[30] + 5.35659e-05 beta[31]
   - 0.0226792328326137 beta[32] - 0.0129344217670589 beta[33]
   - 0.00448036276586319 beta[34] - 0.00158752653326266 beta[35]
   - 6.303314633789894e-04 beta[36] - 2.8682566946855144e-04 beta[37]
   - 1.4822274432083724e-04 beta[38] - 8.49719e-05 beta[39]
   + 0.1283440562123862 beta[40] + 0.0265192179845431 beta[41]
   + 0.00657910559924745 beta[42] + 0.00198865206510621 beta[43]
   + 7.3091962579995039e-04 beta[44] + 0.000319373 beta[45]
   + 1.6062538921698461e-04 beta[46] + 9.00958e-05 beta[47]
   - 0.177388288748607 beta[48] - 0.0268403809963913 beta[49]
   - 0.00571789 beta[50] - 0.00155861692432049 beta[51]
   - 5.2972078309139513e-04 beta[52] - 2.1914562058250475e-04 beta[53]
   - 1.0659339005813106e-04 beta[54] - 5.87703e-05 beta[55]
   + 0.1594305616160333 beta[56] + 0.0197443437989412 beta[57]
   + 0.0034350289085978 beta[58] + 7.303104008796877e-04 beta[59]
   + 0.000179708 beta[60] + 5.00605e-05 beta[61] + 1.57513e-05 beta[62]
   + 5.74371e-06 beta[63] - 0.0647092289652345 beta[64]
   - 0.0071160026913817 beta[65] - 5.7989044084634804e-04 beta[66]
   + 1.3817374171062055e-04 beta[67] + 1.4335017226670564e-04 beta[68]
   + 9.24318e-05 beta[69] + 5.68956e-05 beta[70] + 3.58334e-05 beta[71]
   + 0.0043373403089639 beta[72] - 0.00372532361369164 beta[73]
   - 0.00176600630420798 beta[74] - 7.1629211957274102e-04 beta[75]
   - 3.0188376924305816e-04 beta[76] - 0.000140463 beta[77]
   - 7.31795e-05 beta[78] - 4.2284e-05 beta[79]
   + 0.00653502156203013 beta[80] + 0.00687859956227975 beta[81]
   + 0.00237394730032789 beta[82] + 7.5160818043775455e-04 beta[83]
   + 2.5113289297382899e-04 beta[84] + 9.36298e-05 beta[85]
   + 4.01002e-05 beta[86] + 1.99429e-05 beta[87]
   - 0.0112364059493428 beta[88] - 0.00447074825627922 beta[89]
   - 0.0013271961751196 beta[90] - 3.2452279102322749e-04 beta[91]
   - 6.60175e-05 beta[92] - 5.89658e-06 beta[93] + 5.75458e-06 beta[94]
   + 6.37435e-06 beta[95] + 0.010289039912553 beta[96]
   - 9.1777124324078044e-04 beta[97] - 0.00144675313799158 beta[98]
   - 9.2668913707739053e-04 beta[99] - 5.2541122642105231e-04 beta[100]
   - 2.9284136255086862e-04 beta[101] - 0.000164989 beta[102]
   - 9.44689e-05 beta[103] + 0.0118501841712516 beta[104]
   + 0.00148230893164411 beta[105] + 1.3742727884315164e-04 beta[106]
   - 3.00073e-05 beta[107] - 2.88789e-05 beta[108] - 1.44424e-05 beta[109]
   - 6.09994e-06 beta[110] - 2.69656e-06 beta[111]
   + 0.0031186716636445 beta[112] + 0.00144389061980711 beta[113]
   + 0.000869783 beta[114] + 4.8642329319824638e-04 beta[115]
   + 2.6713130026109234e-04 beta[116] + 1.4872352129735741e-04 beta[117]
   + 8.51285e-05 beta[118] + 5.03588e-05 beta[119]
   - 0.00999629428599696 beta[120] - 0.00203058506023881 beta[121]
   - 4.7777576560897769e-04 beta[122] - 0.000137618 beta[123]
   - 5.6196e-05 beta[124] - 3.22392e-05 beta[125] - 2.18068e-05 beta[126]
   - 1.53649e-05 beta[127] - 0.0048815788415935 beta[128]
   - 9.8825353229096383e-04 beta[129] - 0.000398024 beta[130]
   - 2.0544013251628981e-04 beta[131] - 1.1489018700875651e-04 beta[132]
   - 6.69335e-05 beta[133] - 4.0477e-05 beta[134] - 2.55003e-05 beta[135]
   + 6.4387865793237022e-04 beta[136] + 0.00106546395278239 beta[137]
   + 4.7008332037254169e-04 beta[138] + 2.2260623136130723e-04 beta[139]
   + 0.000125541 beta[140] + 8.12438e-05 beta[141] + 5.69356e-05 beta[142]
   + 4.16833e-05 beta[143] - 0.000244034 beta[144]
   - 1.3713469935019458e-04 beta[145] - 1.542192285651951e-04 beta[146]
   - 0.000113074 beta[147] - 7.78259e-05 beta[148] - 5.51038e-05 beta[149]
   - 4.08083e-05 beta[150] - 3.1421e-05 beta[151]
   + 0.00533385804040292 beta[152] + 6.9329745414556517e-04 beta[153]
   + 1.1225938570835661e-04 beta[154] + 1.96682e-05 beta[155]
   - 7.72038e-07 beta[156] - 6.33293e-06 beta[157] - 7.31075e-06 beta[158]
   - 6.61435e-06 beta[159] + 0.00222369838939733 beta[160]
   + 0.000106534 beta[161] + 5.28215e-05 beta[162] + 6.86506e-05 beta[163]
   + 6.54841e-05 beta[164] + 5.57019e-05 beta[165] + 4.57949e-05 beta[166]
   + 3.7429e-05 beta[167] - 0.0021067065433727 beta[168]
   - 7.8043759441173005e-04 beta[169] - 2.8380338297644733e-04 beta[170]
   - 0.000137144 beta[171] - 8.23134e-05 beta[172] - 5.58224e-05 beta[173]
   - 4.07248e-05 beta[174] - 3.1277e-05 beta[175]
   - 9.6223780546200515e-04 beta[176] + 2.114898069984123e-04 beta[177]
   + 0.000198399 beta[178] + 1.0792153231253276e-04 beta[179]
   + 5.36495e-05 beta[180] + 2.61249e-05 beta[181] + 1.25446e-05 beta[182]
   + 5.84143e-06 beta[183] - 0.00229298097823568 beta[184]
   - 0.000262349 beta[185] - 5.56303e-05 beta[186] - 1.23732e-05 beta[187]
   + 4.30023e-06 beta[188] + 1.10582e-05 beta[189] + 1.31687e-05 beta[190]
   + 1.31989e-05 beta[191] + 0.00488248552159539 beta[192]
   - 0.00243479975961284 beta[193] - 0.00487370889396319 beta[194]
   + 0.00152819785504152 beta[195] + 0.00595692267079287 beta[196]
   + 9.3537453387467287e-04 beta[197] - 0.00541046645100846 beta[198]
   - 0.0030432919838729 beta[199] - 0.00343768392591812 beta[200]
   + 0.00213152830586443 beta[201] + 0.00376113 beta[202]
   - 0.00144107800859389 beta[203] - 0.0047936747988731 beta[204]
   - 5.7401684825398257e-04 beta[205] + 0.0044679483355734 beta[206]
   + 0.00236015419750552 beta[207] + 0.00270092374935201 beta[208]
   - 0.00143571500198562 beta[209] - 0.00262103023955015 beta[210]
   + 0.00108685226845885 beta[211] + 0.00322588494628269 beta[212]
   + 9.17993e-05 beta[213] - 0.0030801692563212 beta[214]
   - 0.00118345430642438 beta[215] + 0.00387284409886831 beta[216]
   + 6.1284477931683294e-04 beta[217] - 0.00164625667510017 beta[218]
   - 7.0245861668044834e-04 beta[219] + 9.3208849727577803e-04 beta[220]
   + 0.000615483 beta[221] - 0.000595139 beta[222]
   - 5.3961432775573943e-04 beta[223] - 0.00615714790263759 beta[224]
   + 2.4888584291637896e-04 beta[225] + 0.00366256517793672 beta[226]
   + 0.000147657 beta[227] - 0.00332958049824241 beta[228]
   - 9.7263763053164257e-04 beta[229] + 0.0028612230927237 beta[230]
   + 0.0018134005204085 beta[231] + 0.00178312486319587 beta[232]
   - 0.00102212204090642 beta[233] - 0.00195101453826432 beta[234]
   + 6.4249842800433231e-04 beta[235] + 0.0025529060687958 beta[236]
   + 4.9486924877014955e-04 beta[237] - 0.00246680472643445 beta[238]
   - 0.00168971376290928 beta[239] + 6.14125e-05 beta[240]
   + 0.0012977919319346 beta[241] + 9.72500265229674e-04 beta[242]
   - 0.00114387712070189 beta[243] - 0.0017787355534353 beta[244]
   + 0.000315145 beta[245] + 0.00194398908788438 beta[246]
   + 5.785498183831948e-04 beta[247] - 0.00322220306767887 beta[248]
   - 0.00101974447441536 beta[249] + 0.00108945555131532 beta[250]
   + 0.00114219797676764 beta[251] - 2.8296769587527674e-04 beta[252]
   - 0.000991781 beta[253] - 1.2309336490722085e-04 beta[254]
   + 8.2923034648813151e-04 beta[255] + 0.00596658694680342 beta[256]
   + 0.000384802 beta[257] - 0.0030730317614227 beta[258]
   - 6.6593384057427442e-04 beta[259] + 0.0024607533563157 beta[260]
   + 0.00114710592100651 beta[261] - 0.00198861729404233 beta[262]
   - 0.00170181465947756 beta[263] - 0.00414141301682439 beta[264]
   + 0.000386536 beta[265] + 0.00258985017700349 beta[266]
   - 0.000197139 beta[267] - 0.00260793777765152 beta[268]
   - 5.0120219714935941e-04 beta[269] + 0.00244645560228767 beta[270]
   + 0.00133983320785663 beta[271] - 0.000403697 beta[272]
   - 9.1936477902882798e-04 beta[273] - 3.9902731680437975e-04 beta[274]
   + 9.7746932099251373e-04 beta[275] + 0.00107315141891842 beta[276]
   - 5.0334718430795737e-04 beta[277] - 0.00134690841039674 beta[278]
   - 1.0904013802783032e-04 beta[279] + 0.00467091315439776 beta[280]
   + 9.3276184439169247e-04 beta[281] - 0.00195810509734029 beta[282]
   - 0.00118087963606003 beta[283] + 0.000969799 beta[284]
   + 0.00111826598064586 beta[285] - 4.3081352628892861e-04 beta[286]
   - 0.000996824 beta[287] + 0.0056716950065746 beta[288]
   + 0.00240559706858647 beta[289] + 0.0143277926311958 beta[290]
   + 5.02603e-06 beta[291] + weighted_residual[10] = 0.0171719495869786
 R601: 0.0637298748269426 beta[0] - 0.00737107051675353 beta[1]
   - 0.00487697478228823 beta[2] - 0.00206585222747187 beta[3]
   - 8.7078947399309506e-04 beta[4] - 3.9859679087540014e-04 beta[5]
   - 0.000203042 beta[6] - 0.000114583 beta[7] + 0.0459006792344303 beta[8]
   + 0.0172941485476269 beta[9] + 0.00565686839637505 beta[10]
   + 0.0019454144596472 beta[11] + 7.4317576964310359e-04 beta[12]
   + 3.2289713931620088e-04 beta[13] + 1.598404814475172e-04 beta[14]
   + 8.8778e-05 beta[15] - 0.1313956048789132 beta[16]
   - 0.02237435048429 beta[17] - 0.00492563197290574 beta[18]
   - 0.00128912457221943 beta[19] - 4.0473276844454615e-04 beta[20]
   - 0.000154866 beta[21] - 7.16712e-05 beta[22] - 3.88274e-05 beta[23]
   + 0.1081663969511466 beta[24] + 0.0129825126281344 beta[25]
   + 0.00150630106262793 beta[26] + 3.15125e-05 beta[27]
   - 9.44313e-05 beta[28] - 6.48736e-05 beta[29] - 3.6297e-05 beta[30]
   - 1.9907e-05 beta[31] - 0.0243789120885447 beta[32]
   + 0.00356104376094652 beta[33] + 0.00256768950974999 beta[34]
   + 0.00112533117025275 beta[35] + 4.7830581896610841e-04 beta[36]
   + 2.1579612988644741e-04 beta[37] + 1.0622333950406875e-04 beta[38]
   + 5.71837e-05 beta[39] - 0.0469445426400225 beta[40]
   - 0.0142469774652389 beta[41] - 0.00429258 beta[42]
   - 0.00136595497809508 beta[43] - 4.8503214994461086e-04 beta[44]
   - 1.9841643242664457e-04 beta[45] - 9.41126e-05 beta[46]
   - 5.09082e-05 beta[47] + 0.0809634994502105 beta[48]
   + 0.0143790064467432 beta[49] + 0.00297683143558655 beta[50]
   + 6.6241529447929497e-04 beta[51] + 1.6118810820407058e-04 beta[52]
   + 4.76028e-05 beta[53] + 1.98474e-05 beta[54] + 1.17581e-05 beta[55]
   - 0.0594734901340185 beta[56] - 0.0061771047246751 beta[57]
   - 0.000200897 beta[58] + 0.000288922 beta[59]
   + 1.9096382778238679e-04 beta[60] + 9.83679e-05 beta[61]
   + 4.88359e-05 beta[62] + 2.46792e-05 beta[63]
   - 0.0161278102941831 beta[64] - 0.00570411115149645 beta[65]
   - 0.00219626336624652 beta[66] - 8.3557433736113139e-04 beta[67]
   - 0.000327417 beta[68] - 1.3784320713111365e-04 beta[69]
   - 6.39204e-05 beta[70] - 3.28392e-05 beta[71]
   + 0.081723422781496 beta[72] + 0.0134183647796112 beta[73]
   + 0.00295248518744649 beta[74] + 0.00076824 beta[75]
   + 2.2747116843181556e-04 beta[76] + 7.86724e-05 beta[77]
   + 3.31554e-05 beta[78] + 1.71251e-05 beta[79]
   - 0.0804620361779166 beta[80] - 0.0109631767824181 beta[81]
   - 0.00167937701448367 beta[82] - 0.000236106 beta[83]
   - 1.36408e-05 beta[84] + 1.01611e-05 beta[85] + 6.47176e-06 beta[86]
   + 2.21091e-06 beta[87] + 0.0307852970661779 beta[88]
   + 0.00149562629459698 beta[89] - 0.000554107 beta[90]
   - 3.5859467620319094e-04 beta[91] - 1.5962922802963668e-04 beta[92]
   - 6.60631e-05 beta[93] - 2.71898e-05 beta[94] - 1.13615e-05 beta[95]
   + 0.00786884823123726 beta[96] + 0.00171571562418459 beta[97]
   + 0.000390886 beta[98] + 4.86654e-05 beta[99] - 3.85067e-05 beta[100]
   - 5.44789e-05 beta[101] - 5.12503e-05 beta[102] - 4.3953e-05 beta[103]
   - 0.000914883 beta[104] + 4.58286e-05 beta[105] + 0.000186806 beta[106]
   + 1.6602739853786183e-04 beta[107] + 1.2434717889545592e-04 beta[108]
   + 8.98226e-05 beta[109] + 6.51969e-05 beta[110] + 4.82705e-05 beta[111]
   - 0.00421484744662288 beta[112] - 0.00141564049184158 beta[113]
   - 6.0555289420770894e-04 beta[114] - 2.9478974720864809e-04 beta[115]
   - 1.5807948512630831e-04 beta[116] - 9.18506e-05 beta[117]
   - 5.71301e-05 beta[118] - 3.76547e-05 beta[119]
   + 0.00245533274133996 beta[120] + 8.2465981494469977e-04 beta[121]
   + 2.8793584820812121e-04 beta[122] + 1.0096045571007244e-04 beta[123]
   + 3.39186e-05 beta[124] + 9.72574e-06 beta[125] + 1.20329e-06 beta[126]
   - 1.53189e-06 beta[127] + 0.000879119 beta[128]
   + 5.4740929915853638e-04 beta[129] + 3.4837355429774076e-04 beta[130]
   + 0.000221806 beta[131] + 1.4346246971302649e-04 beta[132]
   + 9.49143e-05 beta[133] + 6.44327e-05 beta[134] + 4.49237e-05 beta[135]
   - 0.00126440539147057 beta[136] - 8.8796064410758371e-04 beta[137]
   - 5.0522533596829332e-04 beta[138] - 2.8634666101304246e-04 beta[139]
   - 1.6880644867208779e-04 beta[140] - 1.0467919580447583e-04 beta[141]
   - 6.8346e-05 beta[142] - 4.68278e-05 beta[143]
   + 0.00149680334763235 beta[144] + 0.000496599 beta[145]
   + 0.0001924 beta[146] + 7.77682e-05 beta[147] + 3.2092e-05 beta[148]
   + 1.38726e-05 beta[149] + 6.77973e-06 beta[150] + 4.15396e-06 beta[151]
   - 0.00186249402063958 beta[152] - 0.000207998 beta[153]
   + 7.50769e-05 beta[154] + 1.0349829851115546e-04 beta[155]
   + 8.51764e-05 beta[156] + 6.30608e-05 beta[157] + 4.53746e-05 beta[158]
   + 3.25562e-05 beta[159] - 2.9019222731821611e-04 beta[160]
   - 2.6335788429943113e-04 beta[161] - 2.0687151119410738e-04 beta[162]
   - 1.4122628002584276e-04 beta[163] - 9.26051e-05 beta[164]
   - 6.10184e-05 beta[165] - 4.12325e-05 beta[166] - 2.88187e-05 beta[167]
   + 0.00229674454628406 beta[168] + 7.5405920511436545e-04 beta[169]
   + 0.000285193 beta[170] + 0.00011757 beta[171] + 5.05116e-05 beta[172]
   + 2.21655e-05 beta[173] + 9.92485e-06 beta[174] + 4.6462e-06 beta[175]
   - 0.00146647852451159 beta[176] - 5.0045950343358039e-04 beta[177]
   - 1.5356820352433652e-04 beta[178] - 3.64101e-05 beta[179]
   + 9.65609e-07 beta[180] + 1.10049e-05 beta[181] + 1.2021e-05 beta[182]
   + 1.04145e-05 beta[183] + 7.93868e-05 beta[184]
   - 1.7008532561276019e-04 beta[185] - 1.3760635722131443e-04 beta[186]
   - 9.17319e-05 beta[187] - 5.78435e-05 beta[188] - 3.58949e-05 beta[189]
   - 2.23354e-05 beta[190] - 1.40963e-05 beta[191]
   + 0.00531047537195336 beta[192] - 0.00140665030279479 beta[193]
   - 0.00454669436389126 beta[194] + 1.6865049411389645e-04 beta[195]
   + 0.00466058347649112 beta[196] + 0.00179533554357868 beta[197]
   - 0.00360064558257092 beta[198] - 0.00312495834075475 beta[199]
   - 5.5378438077829419e-04 beta[200] + 0.00110277155422021 beta[201]
   + 0.00155898166297601 beta[202] - 2.7774264779705134e-04 beta[203]
   - 0.0018591539962771 beta[204] - 8.6538237139209399e-04 beta[205]
   + 0.00123715770556895 beta[206] + 0.00142895405973079 beta[207]
   - 0.00342750659046147 beta[208] - 5.6642620949555196e-04 beta[209]
   + 0.0012589642992164 beta[210] + 2.6236764261463132e-04 beta[211]
   - 9.6227165432461478e-04 beta[212] - 1.5865432287315482e-04 beta[213]
   + 0.00107727279194519 beta[214] + 0.000478968 beta[215]
   + 0.00185448251171055 beta[216] - 4.01295e-05 beta[217]
   - 0.00107677897141848 beta[218] + 3.79408e-05 beta[219]
   + 0.00125122079071771 beta[220] + 4.6444683035541965e-04 beta[221]
   - 0.00118548419598956 beta[222] - 0.00113680353980014 beta[223]
   + 0.0010147422327648 beta[224] + 3.9513618171749108e-04 beta[225]
   - 0.000164353 beta[226] - 3.2920731232420652e-04 beta[227]
   - 3.2661759966806452e-04 beta[228] - 1.9226277342424737e-04 beta[229]
   + 2.4956029431761375e-04 beta[230] + 6.1468446815018626e-04 beta[231]
   - 0.00109157189355368 beta[232] - 3.4061678950396846e-04 beta[233]
   + 3.1762826929907797e-04 beta[234] + 2.9539589035601559e-04 beta[235]
   - 4.71741e-05 beta[236] - 6.00715e-05 beta[237]
   + 1.87748883426957e-04 beta[238] + 9.91175e-05 beta[239]
   + 9.037571555904067e-04 beta[240] + 1.1329810740049336e-04 beta[241]
   - 0.000413178 beta[242] - 9.17344e-05 beta[243]
   + 3.805687987771291e-04 beta[244] + 1.3226711189627394e-04 beta[245]
   - 5.063576923788638e-04 beta[246] - 4.7079066044276646e-04 beta[247]
   - 8.1970558716081758e-04 beta[248] + 4.62378e-05 beta[249]
   + 4.6626358791638139e-04 beta[250] - 6.853e-05 beta[251]
   - 0.000520205 beta[252] - 7.13717e-05 beta[253]
   + 5.783132166217455e-04 beta[254] + 4.1347265764825065e-04 beta[255]
   - 5.6803034880639834e-04 beta[256] - 1.2007261917959885e-04 beta[257]
   + 2.4578636332591445e-04 beta[258] + 1.8481722546413902e-04 beta[259]
   - 6.38285e-05 beta[260] - 1.1889375945703398e-04 beta[261]
   - 1.06495e-05 beta[262] - 2.08385e-05 beta[263]
   + 0.0016554809466764 beta[264] + 1.0552126698077105e-04 beta[265]
   - 8.4997025986031721e-04 beta[266] - 2.0060538474949558e-04 beta[267]
   + 6.144147736262493e-04 beta[268] + 0.000241721 beta[269]
   - 5.1813724457755255e-04 beta[270] - 3.0223032165897079e-04 beta[271]
   - 7.0032575529538604e-04 beta[272] + 1.35094e-05 beta[273]
   + 0.000410315 beta[274] + 3.86619e-05 beta[275]
   - 3.5029487600306438e-04 beta[276] - 9.45791e-05 beta[277]
   + 3.4253338884790164e-04 beta[278] + 0.000209825 beta[279]
   - 0.00113151416618224 beta[280] - 0.000132303 beta[281]
   + 0.00051132 beta[282] + 1.5630521782504389e-04 beta[283]
   - 0.000333048 beta[284] - 1.625216400791346e-04 beta[285]
   + 0.00021363 beta[286] + 1.107615519714371e-04 beta[287]
   + 0.0570158454763971 beta[288] + 6.8067837228926787e-04 beta[289]
   + 0.00997484725313472 beta[290] + 8.88976e-09 beta[291]
   + weighted_residual[11] = 0.0652133222435025
 R602: 0.0420718751251958 beta[0] - 0.0045957282953249 beta[1]
   - 0.00363740549570787 beta[2] - 0.00174279046155568 beta[3]
   - 8.0557752666797467e-04 beta[4] - 3.908694344613468e-04 beta[5]
   - 2.0476636815206187e-04 beta[6] - 1.1636882787745965e-04 beta[7]
   + 0.0281686114340684 beta[8] + 0.0134494025497539 beta[9]
   + 0.00498364562216627 beta[10] + 0.00192111497995851 beta[11]
   + 8.0228472951750262e-04 beta[12] + 0.000368557 beta[13]
   + 1.8685959909816601e-04 beta[14] + 0.000103869 beta[15]
   - 0.0891751793934958 beta[16] - 0.0200543373924738 beta[17]
   - 0.0054978389422727 beta[18] - 0.0017491313611957 beta[19]
   - 6.4038720018701493e-04 beta[20] - 2.6887219831164805e-04 beta[21]
   - 1.2816780022313501e-04 beta[22] - 6.82199e-05 beta[23]
   + 0.0983308167771314 beta[24] + 0.017370763573036 beta[25]
   + 0.00375863295110178 beta[26] + 9.1272869538350481e-04 beta[27]
   + 2.4492929805426547e-04 beta[28] + 7.2755e-05 beta[29]
   + 2.40085e-05 beta[30] + 8.82372e-06 beta[31]
   - 0.0771034230265695 beta[32] - 0.00901929 beta[33] - 0.0007944 beta[34]
   + 1.9939970079643407e-04 beta[35] + 0.000213105 beta[36]
   + 1.3635622440059695e-04 beta[37] + 8.1337e-05 beta[38]
   + 4.90698e-05 beta[39] + 0.0454262031661285 beta[40]
   + 0.00105434916523376 beta[41] - 0.00149369144143491 beta[42]
   - 0.000919189 beta[43] - 4.6435439718559669e-04 beta[44]
   - 2.3486760639633382e-04 beta[45] - 1.2478742262159864e-04 beta[46]
   - 7.04531e-05 beta[47] - 0.013588518642314 beta[48]
   + 0.00373949850313786 beta[49] + 0.00226620521049919 beta[50]
   + 9.7724839297452923e-04 beta[51] + 4.122683057206403e-04 beta[52]
   + 0.000183196 beta[53] + 8.78994e-05 beta[54] + 4.57833e-05 beta[55]
   + 0.00191079560362885 beta[56] - 0.00397234 beta[57]
   - 0.00165298327431586 beta[58] - 5.5055316965861253e-04 beta[59]
   - 1.7067765990589237e-04 beta[60] - 4.90402e-05 beta[61]
   - 1.12903e-05 beta[62] - 1.84335e-07 beta[63]
   - 0.0130595153830415 beta[64] + 0.000164877 beta[65]
   + 0.000179274 beta[66] - 6.11728e-05 beta[67] - 9.90136e-05 beta[68]
   - 7.80073e-05 beta[69] - 5.28391e-05 beta[70] - 3.44308e-05 beta[71]
   + 0.0251559210301661 beta[72] + 0.0038332444677679 beta[73]
   + 0.0011760263886997 beta[74] + 5.3915047850854514e-04 beta[75]
   + 0.000274419 beta[76] + 0.000144507 beta[77] + 7.85149e-05 beta[78]
   + 4.42543e-05 beta[79] - 0.02118757189953 beta[80]
   - 0.00423610915598346 beta[81] - 0.00142860829066817 beta[82]
   - 6.0473037527518359e-04 beta[83] - 2.7342588357234581e-04 beta[84]
   - 0.000127776 beta[85] - 6.1759e-05 beta[86] - 3.10061e-05 beta[87]
   - 0.00213483280477839 beta[88] + 4.8565375206310364e-04 beta[89]
   + 0.000454682 beta[90] + 2.4199911272638632e-04 beta[91]
   + 1.0481420115565329e-04 beta[92] + 4.01864e-05 beta[93]
   + 1.3423e-05 beta[94] + 3.18585e-06 beta[95]
   + 0.00628817583131219 beta[96] + 0.00178162646599403 beta[97]
   + 5.7877726109780054e-04 beta[98] + 1.9029968841110872e-04 beta[99]
   + 5.39262e-05 beta[100] + 5.37971e-06 beta[101] - 1.11234e-05 beta[102]
   - 1.57966e-05 beta[103] - 0.00100483741616053 beta[104]
   - 2.2143623180927743e-04 beta[105] - 2.96797e-06 beta[106]
   + 5.39388e-05 beta[107] + 6.07338e-05 beta[108] + 5.34405e-05 beta[109]
   + 4.37689e-05 beta[110] + 3.51474e-05 beta[111]
   - 0.00235202127396284 beta[112] - 9.9643110133347751e-04 beta[113]
   - 4.9312349047440029e-04 beta[114] - 2.7338631021608131e-04 beta[115]
   - 1.6473760728412024e-04 beta[116] - 0.000106138 beta[117]
   - 7.22123e-05 beta[118] - 5.13606e-05 beta[119]
   + 0.00125407015289273 beta[120] + 6.9234127115497832e-04 beta[121]
   + 3.6163476708314527e-04 beta[122] + 1.9505155398593949e-04 beta[123]
   + 1.1097027794921066e-04 beta[124] + 6.70549e-05 beta[125]
   + 4.29823e-05 beta[126] + 2.90534e-05 beta[127]
   - 1.8287263034111876e-04 beta[128] + 7.68468e-05 beta[129]
   + 8.349e-05 beta[130] + 6.97272e-05 beta[131] + 5.51905e-05 beta[132]
   + 4.29949e-05 beta[133] + 3.34265e-05 beta[134] + 2.61219e-05 beta[135]
   + 1.9568234955099877e-04 beta[136] - 2.7037560570024045e-04 beta[137]
   - 2.5272737471878189e-04 beta[138] - 1.8901840321067012e-04 beta[139]
   - 1.3664588226294032e-04 beta[140] - 9.9523e-05 beta[141]
   - 7.3863e-05 beta[142] - 5.59884e-05 beta[143]
   + 8.0873334709104575e-04 beta[144] + 3.3441129731175324e-04 beta[145]
   + 0.000197151 beta[146] + 1.2803125301545914e-04 beta[147]
   + 8.66152e-05 beta[148] + 6.0535e-05 beta[149] + 4.36585e-05 beta[150]
   + 3.24398e-05 beta[151] - 0.00111553983985561 beta[152]
   - 4.0134630864825828e-04 beta[153] - 1.5478269540313775e-04 beta[154]
   - 6.1369e-05 beta[155] - 2.288e-05 beta[156] - 6.17976e-06 beta[157]
   + 1.14493e-06 beta[158] + 4.2097e-06 beta[159] - 3.88653e-05 beta[160]
   + 6.23979e-05 beta[161] + 2.48285e-05 beta[162] - 3.34432e-06 beta[163]
   - 1.58451e-05 beta[164] - 1.98069e-05 beta[165] - 1.98981e-05 beta[166]
   - 1.84274e-05 beta[167] + 6.1597016738777289e-04 beta[168]
   + 3.3433186628692674e-04 beta[169] + 1.7603244665386806e-04 beta[170]
   + 1.0138554594698617e-04 beta[171] + 6.3582e-05 beta[172]
   + 4.25212e-05 beta[173] + 2.98066e-05 beta[174] + 2.16495e-05 beta[175]
   - 7.5664228407435743e-04 beta[176] - 3.774868709167336e-04 beta[177]
   - 2.2060778330496993e-04 beta[178] - 1.3327826979291568e-04 beta[179]
   - 8.30667e-05 beta[180] - 5.31942e-05 beta[181] - 3.48072e-05 beta[182]
   - 2.31507e-05 beta[183] + 5.7489657032050413e-04 beta[184]
   + 1.9936484519030224e-04 beta[185] + 9.43192e-05 beta[186]
   + 5.41055e-05 beta[187] + 3.38153e-05 beta[188] + 2.18976e-05 beta[189]
   + 1.43883e-05 beta[190] + 9.49885e-06 beta[191]
   + 0.00405186617889774 beta[192] - 0.00107508878422918 beta[193]
   - 0.00370435289612191 beta[194] - 0.000287132 beta[195]
   + 0.00356778156576738 beta[196] + 0.00208197535059204 beta[197]
   - 0.00216443230288663 beta[198] - 0.00288256400582749 beta[199]
   - 5.3413422697446626e-04 beta[200] + 8.8529735939455649e-04 beta[201]
   + 0.00146336694056186 beta[202] + 6.24073e-05 beta[203]
   - 0.00155077849123741 beta[204] - 0.00117306795400458 beta[205]
   + 6.8339381204135746e-04 beta[206] + 0.00150409361293727 beta[207]
   - 0.00190559179677726 beta[208] - 5.4074425315938886e-04 beta[209]
   + 4.3468428129765657e-04 beta[210] + 0.000159287 beta[211]
   - 2.9731445106651191e-04 beta[212] + 3.99825e-05 beta[213]
   + 5.0894641513031503e-04 beta[214] + 1.7229618889449415e-04 beta[215]
   + 0.00141595322189216 beta[216] + 1.2330379186623855e-04 beta[217]
   - 7.4056117717810805e-04 beta[218] - 1.5469642963403718e-04 beta[219]
   + 8.0507262585695967e-04 beta[220] + 5.7744221015943408e-04 beta[221]
   - 5.9662132080845855e-04 beta[222] - 0.00102260131298466 beta[223]
   - 5.0273559312595929e-04 beta[224] + 1.8951011273260477e-04 beta[225]
   + 0.000546822 beta[226] - 4.02813e-06 beta[227]
   - 7.2462846069867339e-04 beta[228] - 5.6209926379931273e-04 beta[229]
   + 3.6993015751413171e-04 beta[230] + 8.8438768469744939e-04 beta[231]
   - 3.2352077998653764e-04 beta[232] - 3.0403625770155946e-04 beta[233]
   - 1.3195081459802096e-04 beta[234] + 0.000160999 beta[235]
   + 0.00032158 beta[236] + 1.9611421351129388e-04 beta[237]
   - 6.94975e-05 beta[238] - 0.000232558 beta[239]
   + 0.00112386595492194 beta[240] + 0.000263327 beta[241]
   - 4.1063458755328229e-04 beta[242] - 0.000239226 beta[243]
   + 0.000240459 beta[244] + 1.9793065622264469e-04 beta[245]
   - 2.8120625502596296e-04 beta[246] - 4.0636953229710701e-04 beta[247]
   - 0.00107617615943911 beta[248] - 1.1539672794566514e-04 beta[249]
   + 5.3903749653827883e-04 beta[250] + 1.6063723754991159e-04 beta[251]
   - 4.7542080728452135e-04 beta[252] - 3.2407271831584096e-04 beta[253]
   + 4.0047653760613147e-04 beta[254] + 6.1700151336884553e-04 beta[255]
   + 4.1638988897710902e-04 beta[256] - 6.15553e-05 beta[257]
   - 0.000288273 beta[258] + 4.09854e-05 beta[259] + 0.000355607 beta[260]
   + 1.3757074054011504e-04 beta[261] - 2.9941444339617689e-04 beta[262]
   - 3.5014123045736472e-04 beta[263] + 0.000659866 beta[264]
   + 1.5670161212789384e-04 beta[265] - 0.000262304 beta[266]
   - 2.0250926969135545e-04 beta[267] + 7.91657e-05 beta[268]
   + 1.3303317704265919e-04 beta[269] - 3.95514e-05 beta[270]
   - 8.22199e-05 beta[271] - 0.00114553085473659 beta[272]
   - 0.000113093 beta[273] + 5.7166261907470677e-04 beta[274]
   + 1.913357799062183e-04 beta[275] - 3.9466133322763687e-04 beta[276]
   - 2.3486137751098173e-04 beta[277] + 3.0923969281209388e-04 beta[278]
   + 3.2109754349170634e-04 beta[279] + 4.7030415413995693e-04 beta[280]
   - 1.31227e-05 beta[281] - 0.000293724 beta[282] - 3.92314e-05 beta[283]
   + 0.000267849 beta[284] + 1.2161649658237709e-04 beta[285]
   - 2.4172016277426226e-04 beta[286] - 2.5497082177251769e-04 beta[287]
   + 0.0392479270918885 beta[288] + 6.8215475354088196e-04 beta[289]
   + 0.00674770796110305 beta[290] - 2.59383e-06 beta[291]
   + weighted_residual[12] = 0.0451783019337006
 R603: - 0.0448156566466839 beta[0] + 0.0138332013000031 beta[1]
   + 0.0116881970569989 beta[2] + 0.00714841626618411 beta[3]
   + 0.00424529046486119 beta[4] + 0.00259235237260766 beta[5]
   + 0.00165316039861689 beta[6] + 0.00110236131727644 beta[7]
   - 0.1077167402685063 beta[8] - 0.0405602537253046 beta[9]
   - 0.0176977315904865 beta[10] - 0.00865348254050226 beta[11]
   - 0.00463135169230378 beta[12] - 0.0026777910298358 beta[13]
   - 0.00165469932510973 beta[14] - 0.00108162015607835 beta[15]
   + 0.2147583961225242 beta[16] + 0.0566205894347339 beta[17]
   + 0.0199474503976505 beta[18] + 0.00851992718723526 beta[19]
   + 0.00419738414307689 beta[20] + 0.00230877606324284 beta[21]
   + 0.00138348736464969 beta[22] + 8.8640639735826214e-04 beta[23]
   - 0.1978264910251409 beta[24] - 0.043924618482735 beta[25]
   - 0.0134807783687672 beta[26] - 0.00520019930341 beta[27]
   - 0.002390913963802 beta[28] - 0.00125912491975744 beta[29]
   - 0.000734797 beta[30] - 0.000463235 beta[31]
   + 0.1095769006108963 beta[32] + 0.0163630185843803 beta[33]
   + 0.00301496901344225 beta[34] + 6.1107978929015173e-04 beta[35]
   + 1.132952096374458e-04 beta[36] + 5.11071e-06 beta[37]
   - 1.56143e-05 beta[38] - 1.6325e-05 beta[39]
   + 0.0020469956206427 beta[40] + 0.00902563469482998 beta[41]
   + 0.00509290063747772 beta[42] + 0.00263673663335738 beta[43]
   + 0.00142213486076485 beta[44] + 8.1878059690123424e-04 beta[45]
   + 0.000502114 beta[46] + 3.2505967428430216e-04 beta[47]
   - 0.0788816250670473 beta[48] - 0.0218570963642461 beta[49]
   - 0.00807466580320758 beta[50] - 0.00358017591094441 beta[51]
   - 0.00180479139231107 beta[52] - 0.001005457981717 beta[53]
   - 6.0585852559154286e-04 beta[54] - 3.8822636974546708e-04 beta[55]
   + 0.0716575922202379 beta[56] + 0.0179609839869996 beta[57]
   + 0.00632690448189126 beta[58] + 0.00275219269515664 beta[59]
   + 0.00137908089680522 beta[60] + 7.6556237400304968e-04 beta[61]
   + 4.5907779105661844e-04 beta[62] + 2.9227378748783304e-04 beta[63]
   + 0.000853824 beta[64] - 0.0046149726078586 beta[65]
   - 0.0026434396825753 beta[66] - 0.00136529810010824 beta[67]
   - 7.3845868081357446e-04 beta[68] - 4.2373131311669392e-04 beta[69]
   - 2.5657371062467587e-04 beta[70] - 1.6280557906747713e-04 beta[71]
   - 0.0606202409193283 beta[72] - 0.0042136581381364 beta[73]
   + 0.000490529 beta[74] + 5.7060877972596089e-04 beta[75]
   + 3.5537781845163072e-04 beta[76] + 2.0864747055553853e-04 beta[77]
   + 1.2437076141303663e-04 beta[78] + 7.65218e-05 beta[79]
   + 0.0443611074324547 beta[80] + 0.00119231837013846 beta[81]
   - 0.00118261809086284 beta[82] - 6.9575651960428414e-04 beta[83]
   - 3.3841568677582957e-04 beta[84] - 1.6497112237003484e-04 beta[85]
   - 8.36083e-05 beta[86] - 4.4329e-05 beta[87]
   + 0.019389422699171 beta[88] + 0.00869513521436703 beta[89]
   + 0.00313897944789925 beta[90] + 0.00113049151353912 beta[91]
   + 4.2908549482271574e-04 beta[92] + 1.7255914300498426e-04 beta[93]
   + 7.26564e-05 beta[94] + 3.14073e-05 beta[95]
   - 0.0233736554365823 beta[96] - 0.00903492597805197 beta[97]
   - 0.00419852366057791 beta[98] - 0.00216823064410918 beta[99]
   - 0.00120884795037788 beta[100] - 7.1823073734696868e-04 beta[101]
   - 0.000450696 beta[102] - 0.000296306 beta[103]
   - 9.5602712692805273e-04 beta[104] - 2.2910627359874481e-04 beta[105]
   - 2.5177568577034051e-04 beta[106] - 0.000269278 beta[107]
   - 2.5690969424773367e-04 beta[108] - 2.3080418611406934e-04 beta[109]
   - 2.0178783263153131e-04 beta[110] - 1.746806341983557e-04 beta[111]
   + 0.00823698289417643 beta[112] + 0.00449430858974379 beta[113]
   + 0.00264213614530117 beta[114] + 0.00167832072005533 beta[115]
   + 0.00113776882995057 beta[116] + 8.1398554531093999e-04 beta[117]
   + 6.0841814369641252e-04 beta[118] + 4.7111249736787533e-04 beta[119]
   - 0.00273343543791899 beta[120] - 0.00195402106033746 beta[121]
   - 0.00128397083125135 beta[122] - 8.6387118626227199e-04 beta[123]
   - 6.0529071471658667e-04 beta[124] - 4.425586398836411e-04 beta[125]
   - 3.3631126179427875e-04 beta[126] - 0.000264069 beta[127]
   + 0.00206842755146748 beta[128] - 7.84976e-05 beta[129]
   - 0.000319274 beta[130] - 2.8586130622282991e-04 beta[131]
   - 2.2324656996838556e-04 beta[132] - 0.000170788 beta[133]
   - 0.000131618 beta[134] - 1.0296827893312729e-04 beta[135]
   + 0.00121854837538025 beta[136] + 0.00103224621743388 beta[137]
   + 8.3473544702996998e-04 beta[138] + 6.3984270490457964e-04 beta[139]
   + 4.8861557509945869e-04 beta[140] + 3.7886466173100492e-04 beta[141]
   + 0.000299861 beta[142] + 2.4223542606591406e-04 beta[143]
   - 0.00447812200404376 beta[144] - 0.00181516263458829 beta[145]
   - 0.000916829 beta[146] - 5.5116258202111328e-04 beta[147]
   - 3.7144553896229925e-04 beta[148] - 2.7023435342982512e-04 beta[149]
   - 2.0738358061114155e-04 beta[150] - 1.654045918544157e-04 beta[151]
   + 0.00243090894993655 beta[152] + 0.00105060400160093 beta[153]
   + 4.8627841416864516e-04 beta[154] + 2.553742905539637e-04 beta[155]
   + 1.5009870449551988e-04 beta[156] + 9.6869e-05 beta[157]
   + 6.73479e-05 beta[158] + 4.96119e-05 beta[159]
   + 1.2599828026097726e-04 beta[160] + 3.8837823212653722e-04 beta[161]
   + 0.000233125 beta[162] + 1.3613566236218928e-04 beta[163]
   + 8.33911e-05 beta[164] + 5.44166e-05 beta[165] + 3.79464e-05 beta[166]
   + 2.81746e-05 beta[167] - 0.00253615292895697 beta[168]
   - 0.00101767518920466 beta[169] - 5.1549234109254103e-04 beta[170]
   - 2.9093151367757468e-04 beta[171] - 1.760981457600729e-04 beta[172]
   - 0.00011302 beta[173] - 7.64446e-05 beta[174] - 5.41995e-05 beta[175]
   + 0.00251316204326221 beta[176] + 6.93909354173246e-04 beta[177]
   + 0.000254816 beta[178] + 1.1972043422161901e-04 beta[179]
   + 6.82097e-05 beta[180] + 4.44444e-05 beta[181] + 3.15717e-05 beta[182]
   + 2.36789e-05 beta[183] + 0.000676342 beta[184] + 0.000254476 beta[185]
   + 1.8829446460306786e-04 beta[186] + 1.3297883684978322e-04 beta[187]
   + 8.91826e-05 beta[188] + 5.87199e-05 beta[189] + 3.86104e-05 beta[190]
   + 2.55409e-05 beta[191] - 0.012427472124579 beta[192]
   + 0.00254910046008527 beta[193] + 0.0126080883248394 beta[194]
   + 0.00564682130928165 beta[195] - 0.00731680909692034 beta[196]
   - 0.00937787303462029 beta[197] - 3.4330461361794048e-04 beta[198]
   + 0.00637543872115316 beta[199] + 0.00612927893370446 beta[200]
   - 0.00238782883710397 beta[201] - 0.00831445139626297 beta[202]
   - 0.00428473694981485 beta[203] + 0.00411792835250039 beta[204]
   + 0.00661866295287027 beta[205] + 0.00150943466395493 beta[206]
   - 0.0037281742043974 beta[207] + 0.00122642486763739 beta[208]
   + 0.00216016752985884 beta[209] + 0.00288606940594049 beta[210]
   + 0.00205958920731553 beta[211] - 0.000319807 beta[212]
   - 0.00236931374710516 beta[213] - 0.00213198377443927 beta[214]
   - 1.21276e-05 beta[215] - 0.00486022741891348 beta[216]
   - 0.00172264871162879 beta[217] + 6.8153788430798271e-04 beta[218]
   - 5.88353e-05 beta[219] - 0.00181471107473886 beta[220]
   - 0.00127088186008463 beta[221] + 0.00130890415940917 beta[222]
   + 0.00260197721295818 beta[223] + 0.00447584360366684 beta[224]
   + 9.5234476273839332e-04 beta[225] - 0.00187321941552003 beta[226]
   - 8.6594383286710177e-04 beta[227] + 0.00215324782904556 beta[228]
   + 0.00287147647358026 beta[229] + 6.14169e-05 beta[230]
   - 0.002911038935284 beta[231] - 0.00301648210465212 beta[232]
   - 1.1188188007775622e-04 beta[233] + 0.00199830208446965 beta[234]
   + 8.2624036150762527e-04 beta[235] - 0.00184958663359017 beta[236]
   - 0.00261150232472912 beta[237] - 6.843366697692493e-04 beta[238]
   + 0.00163150335322644 beta[239] + 0.00108171630238937 beta[240]
   - 4.8273088651532172e-04 beta[241] - 0.00134897172264744 beta[242]
   - 0.00035572 beta[243] + 0.0011026115967863 beta[244]
   + 0.00141252 beta[245] + 7.5864545671322113e-04 beta[246]
   + 3.79215e-05 beta[247] + 0.002099551085423 beta[248]
   + 7.7608921181330994e-04 beta[249] - 3.1601039463765359e-04 beta[250]
   - 1.9619531544783235e-04 beta[251] + 3.2506857633417296e-04 beta[252]
   - 1.80406e-05 beta[253] - 0.00106408816484439 beta[254]
   - 0.0014095371078279 beta[255] - 0.00387902638257592 beta[256]
   - 7.3920120058892187e-04 beta[257] + 0.00146526847324545 beta[258]
   + 4.7054528994595511e-04 beta[259] - 0.00131970565412518 beta[260]
   - 8.7505125235637967e-04 beta[261] + 0.0011482483308386 beta[262]
   + 0.00195042775639017 beta[263] + 0.00199484416865624 beta[264]
   + 3.6131829512118293e-04 beta[265] - 7.9556566692243799e-04 beta[266]
   - 0.000211567 beta[267] + 0.0009208 beta[268]
   + 8.2474063178107702e-04 beta[269] - 4.5063921669756096e-04 beta[270]
   - 0.00137848506658565 beta[271] + 6.9943261743970228e-04 beta[272]
   + 3.59884e-05 beta[273] - 3.8576077716322258e-04 beta[274]
   - 2.1164527839827912e-04 beta[275] - 6.54319e-05 beta[276]
   - 0.000296894 beta[277] - 0.00030793 beta[278]
   + 3.5813528594828478e-04 beta[279] - 5.762787413831407e-04 beta[280]
   - 0.000103457 beta[281] + 3.0684481734390747e-04 beta[282]
   + 2.7575960157420423e-04 beta[283] + 3.52144e-05 beta[284]
   + 3.83703e-05 beta[285] + 2.6709230409694784e-04 beta[286]
   + 2.1177617996382059e-04 beta[287] - 0.0226220304974003 beta[288]
   - 0.00574275708914975 beta[289] - 0.0421736056107895 beta[290]
   + 2.95978e-07 beta[291] + weighted_residual[13] = -0.0585380816632672
 R604: 0.00404734030029669 beta[0] + 0.00166606988259081 beta[1]
   + 0.00253942830139259 beta[2] + 0.00225704785404438 beta[3]
   + 0.00174803413706879 beta[4] + 0.00129770581399032 beta[5]
   + 9.554957569886727e-04 beta[6] + 0.000708091 beta[7]
   - 0.0213757691396352 beta[8] - 0.00912635941926418 beta[9]
   - 0.0052607823853107 beta[10] - 0.0032620457725639 beta[11]
   - 0.00211207603444364 beta[12] - 0.00141795092462614 beta[13]
   - 9.8368648240519641e-04 beta[14] - 7.0316439133306496e-04 beta[15]
   + 0.0254458950892047 beta[16] + 0.0120600259872297 beta[17]
   + 0.00608787603338528 beta[18] + 0.00335209296779339 beta[19]
   + 0.0019873520051534 beta[20] + 0.00125548534128182 beta[21]
   + 8.3716438050554325e-04 beta[22] + 5.8408787636522914e-04 beta[23]
   - 0.0168790382826147 beta[24] - 0.00781384752065367 beta[25]
   - 0.00379334118276935 beta[26] - 0.0020226789730456 beta[27]
   - 0.00117659099429785 beta[28] - 7.3828830549360982e-04 beta[29]
   - 4.9345480545669629e-04 beta[30] - 3.4706633212303446e-04 beta[31]
   + 0.00379590177505936 beta[32] + 0.002265572008169 beta[33]
   + 0.00113567284292325 beta[34] + 6.171032440148678e-04 beta[35]
   + 3.7493961845845564e-04 beta[36] + 2.497221420157097e-04 beta[37]
   + 1.7751747785489804e-04 beta[38] + 1.3195578695953728e-04 beta[39]
   + 0.00512142182983745 beta[40] + 1.9887727993925155e-04 beta[41]
   - 1.6309650673756293e-04 beta[42] - 1.3670159251397241e-04 beta[43]
   - 9.84679e-05 beta[44] - 7.24159e-05 beta[45] - 5.46972e-05 beta[46]
   - 4.21061e-05 beta[47] - 6.7372655160389974e-04 beta[48]
   + 0.00141540679430491 beta[49] + 8.3771157249771556e-04 beta[50]
   + 4.3892150274988263e-04 beta[51] + 2.3713158865645566e-04 beta[52]
   + 1.3525313310701602e-04 beta[53] + 8.13052e-05 beta[54]
   + 5.11582e-05 beta[55] - 0.0064465437255114 beta[56]
   - 0.00378486494086435 beta[57] - 0.00169997686968715 beta[58]
   - 7.9132349949671311e-04 beta[59] - 3.9702841519731989e-04 beta[60]
   - 2.1453432132507029e-04 beta[61] - 1.2368111381800621e-04 beta[62]
   - 7.52916e-05 beta[63] + 0.00514677030030699 beta[64]
   + 0.00307554159714801 beta[65] + 0.00132273977942367 beta[66]
   + 5.9083828691699038e-04 beta[67] + 2.8999663983892451e-04 beta[68]
   + 1.5657156811818714e-04 beta[69] + 9.17175e-05 beta[70]
   + 5.73538e-05 beta[71] + 0.00447131593958384 beta[72]
   + 0.000440932 beta[73] + 1.5454168083791988e-04 beta[74]
   + 9.26463e-05 beta[75] + 5.26052e-05 beta[76] + 2.75872e-05 beta[77]
   + 1.35191e-05 beta[78] + 6.05397e-06 beta[79]
   - 0.013343675180681 beta[80] - 0.00352035712952727 beta[81]
   - 0.00142231836969426 beta[82] - 0.000687477 beta[83]
   - 3.6373584862794506e-04 beta[84] - 2.0557653647076274e-04 beta[85]
   - 1.2291759274409377e-04 beta[86] - 7.71948e-05 beta[87]
   + 0.0129520227069811 beta[88] + 0.00364763580272922 beta[89]
   + 0.00155014607320984 beta[90] + 7.893205845704175e-04 beta[91]
   + 4.4430337305468654e-04 beta[92] + 2.691276771541165e-04 beta[93]
   + 1.7279828364796478e-04 beta[94] + 1.1626917204614133e-04 beta[95]
   - 0.00859628277153288 beta[96] - 0.00454852950920762 beta[97]
   - 0.00267540052628215 beta[98] - 0.00166375453129128 beta[99]
   - 0.00107244366782657 beta[100] - 7.1015255045981252e-04 beta[101]
   - 0.000480919 beta[102] - 3.322653545841415e-04 beta[103]
   - 0.00238779781623927 beta[104] - 8.6276188758563311e-04 beta[105]
   - 4.8557867305493212e-04 beta[106] - 0.000335465 beta[107]
   - 2.5742776656814562e-04 beta[108] - 2.0885759949747527e-04 beta[109]
   - 1.7478588462095429e-04 beta[110] - 1.4900942345098952e-04 beta[111]
   + 0.00190766639964011 beta[112] + 0.00176089170026281 beta[113]
   + 0.0012946366793937 beta[114] + 9.4569271756117686e-04 beta[115]
   + 7.025253378137845e-04 beta[116] + 0.000533209 beta[117]
   + 4.1374241583794045e-04 beta[118] + 3.2797873615414728e-04 beta[119]
   - 0.000227507 beta[120] - 1.4196415486529408e-04 beta[121]
   - 1.3262256196599318e-04 beta[122] - 1.183823322128522e-04 beta[123]
   - 1.0227559287624437e-04 beta[124] - 8.7559e-05 beta[125]
   - 7.52635e-05 beta[126] - 6.53657e-05 beta[127] + 6.22566e-05 beta[128]
   - 3.3097748501719409e-04 beta[129] - 3.6170641975116909e-04 beta[130]
   - 3.163864725285214e-04 beta[131] - 2.599034724236716e-04 beta[132]
   - 2.0928453197694588e-04 beta[133] - 1.6793874091721703e-04 beta[134]
   - 1.3528528666295863e-04 beta[135] + 0.00162039281221971 beta[136]
   + 0.000723993 beta[137] + 4.2970935002120301e-04 beta[138]
   + 0.000293727 beta[139] + 2.1704813515556815e-04 beta[140]
   + 1.6822083607607308e-04 beta[141] + 1.3469145274177537e-04 beta[142]
   + 1.10507851028463e-04 beta[143] - 3.53424e-05 beta[144]
   - 2.087483770404562e-04 beta[145] - 1.3942964659581112e-04 beta[146]
   - 8.48918e-05 beta[147] - 5.35887e-05 beta[148] - 3.66516e-05 beta[149]
   - 2.75407e-05 beta[150] - 2.2545e-05 beta[151]
   - 6.3108373205677474e-04 beta[152] - 5.017704245787179e-04 beta[153]
   - 3.1520525019543294e-04 beta[154] - 0.000202065 beta[155]
   - 0.000134579 beta[156] - 9.2746e-05 beta[157] - 6.57089e-05 beta[158]
   - 4.7589e-05 beta[159] + 7.2923165642541185e-04 beta[160]
   + 4.4265254138361321e-04 beta[161] + 0.000309562 beta[162]
   + 0.000218705 beta[163] + 1.5673276014824578e-04 beta[164]
   + 1.145558210784614e-04 beta[165] + 8.55765e-05 beta[166]
   + 6.53345e-05 beta[167] - 2.2352239065406119e-04 beta[168]
   - 4.87044e-05 beta[169] - 1.10882e-05 beta[170] - 8.78526e-06 beta[171]
   - 1.24629e-05 beta[172] - 1.56884e-05 beta[173] - 1.75004e-05 beta[174]
   - 1.81305e-05 beta[175] - 8.9037989862111974e-04 beta[176]
   - 0.000409915 beta[177] - 2.4166380119722947e-04 beta[178]
   - 1.568508257640067e-04 beta[179] - 1.0587978635739936e-04 beta[180]
   - 7.27549e-05 beta[181] - 5.04097e-05 beta[182] - 3.50105e-05 beta[183]
   + 4.0122015377832345e-04 beta[184] + 0.000348706 beta[185]
   + 0.000227539 beta[186] + 1.5090563809356427e-04 beta[187]
   + 1.049067979507438e-04 beta[188] + 7.62431e-05 beta[189]
   + 5.74327e-05 beta[190] + 4.4471e-05 beta[191]
   - 0.00389934518277807 beta[192] + 1.1853544345636881e-04 beta[193]
   + 0.00403245159046039 beta[194] + 0.00404155581485998 beta[195]
   + 0.000532875 beta[196] - 0.00278529 beta[197]
   - 0.00306644626026147 beta[198] - 8.9437639261503196e-04 beta[199]
   + 0.0035294543031706 beta[200] - 2.504634432411986e-04 beta[201]
   - 0.00370781501915484 beta[202] - 0.00346597328355703 beta[203]
   - 3.6502438544291178e-04 beta[204] + 0.00224835096961832 beta[205]
   + 0.00242090277245644 beta[206] + 8.80582392248148e-04 beta[207]
   - 0.00197438800157162 beta[208] + 4.9218335791390553e-04 beta[209]
   + 0.00267866387831883 beta[210] + 0.00243065637918789 beta[211]
   + 4.0423227552011429e-04 beta[212] - 0.00129911139914403 beta[213]
   - 0.00159063488067681 beta[214] - 8.6493061175183753e-04 beta[215]
   - 1.1351678293202329e-04 beta[216] - 0.000728992 beta[217]
   - 0.00130402066866104 beta[218] - 0.00123935836652833 beta[219]
   - 5.5330012102408599e-04 beta[220] + 2.6504868409759768e-04 beta[221]
   + 7.5277645356701915e-04 beta[222] + 7.4236276674550519e-04 beta[223]
   + 0.00134795070634845 beta[224] + 8.1620132543922289e-04 beta[225]
   + 3.0605913127025505e-04 beta[226] + 2.4676363273705876e-04 beta[227]
   + 0.000470027 beta[228] + 4.9245063437423746e-04 beta[229]
   + 1.1237055092066926e-04 beta[230] - 4.036623930408265e-04 beta[231]
   - 0.00164267335794559 beta[232] - 0.000720434 beta[233]
   + 2.3523170451849673e-04 beta[234] + 3.8400927899185147e-04 beta[235]
   - 2.3876638043856236e-04 beta[236] - 8.5438128807393762e-04 beta[237]
   - 0.000778448 beta[238] - 4.73251e-05 beta[239]
   + 0.00163283901839763 beta[240] + 0.000517545 beta[241]
   - 5.9145641663635733e-04 beta[242] - 6.9255637384725024e-04 beta[243]
   + 1.1511581296384072e-04 beta[244] + 9.2805516598522687e-04 beta[245]
   + 0.00101957386974744 beta[246] + 3.7954669838320627e-04 beta[247]
   - 0.0014570637873222 beta[248] - 2.7854989519931025e-04 beta[249]
   + 7.9488135417968601e-04 beta[250] + 7.5322261226693258e-04 beta[251]
   - 1.0780680756666113e-04 beta[252] - 8.2554682518264826e-04 beta[253]
   - 9.0190425706228989e-04 beta[254] - 4.9119447094478417e-04 beta[255]
   + 9.5857338024916776e-04 beta[256] + 3.14653e-05 beta[257]
   - 7.5037865491405095e-04 beta[258] - 6.1218810906079691e-04 beta[259]
   + 9.68352e-05 beta[260] + 5.8960825839621321e-04 beta[261]
   + 0.000622208 beta[262] + 4.4991251210851061e-04 beta[263]
   - 0.000205305 beta[264] + 1.9356348254620276e-04 beta[265]
   + 4.8886946981947321e-04 beta[266] + 3.4302529964938913e-04 beta[267]
   - 3.6166e-05 beta[268] - 2.7318174882732306e-04 beta[269]
   - 3.1624159531669924e-04 beta[270] - 0.000348409 beta[271]
   - 4.9094818464197147e-04 beta[272] - 3.4956914453466184e-04 beta[273]
   - 0.000169302 beta[274] - 5.6495e-05 beta[275] - 3.3677e-05 beta[276]
   - 3.43969e-05 beta[277] + 3.94813e-05 beta[278]
   + 2.3091334024153313e-04 beta[279] + 8.8594878234271384e-04 beta[280]
   + 0.000404863 beta[281] - 7.46678e-05 beta[282]
   - 1.5523875779373372e-04 beta[283] + 7.75686e-05 beta[284]
   + 2.5941550277967882e-04 beta[285] + 1.7342286819381587e-04 beta[286]
   - 0.000120205 beta[287] + 0.00917241390034642 beta[288]
   - 0.00490158778968065 beta[289] - 0.0202565684354302 beta[290]
   + 2.56064e-07 beta[291] + weighted_residual[14] = -0.00859389399891641
 R605: - 0.0936400833353675 beta[0] - 0.00627033460747546 beta[1]
   + 0.00520288716552977 beta[2] + 0.00537069050537928 beta[3]
   + 0.00393057853599226 beta[4] + 0.00268230300162538 beta[5]
   + 0.00182133404661219 beta[6] + 0.00125884860111203 beta[7]
   - 0.00371812751447107 beta[8] - 0.015860773606196 beta[9]
   - 0.0103969131345358 beta[10] - 0.00624498200996233 beta[11]
   - 0.00378261695258854 beta[12] - 0.00236729938732763 beta[13]
   - 0.00154181155271027 beta[14] - 0.00104551676042727 beta[15]
   + 0.0784404679208462 beta[16] + 0.0309989432533795 beta[17]
   + 0.0126080874417939 beta[18] + 0.00566353700208204 beta[19]
   + 0.00285271443717906 beta[20] + 0.00159993722042882 beta[21]
   + 9.8372440783293133e-04 beta[22] + 6.5111562654976678e-04 beta[23]
   - 0.061665778111175 beta[24] - 0.01964004828729 beta[25]
   - 0.00639548457099949 beta[26] - 0.00223625670449086 beta[27]
   - 8.8749455053794169e-04 beta[28] - 4.2054447768812394e-04 beta[29]
   - 2.4171816110438616e-04 beta[30] - 1.6256488210521393e-04 beta[31]
   - 0.01437279110346 beta[32] - 0.00877925298269037 beta[33]
   - 0.00469384879442772 beta[34] - 0.00252196489839874 beta[35]
   - 0.00138441140691493 beta[36] - 7.8448626324330772e-04 beta[37]
   - 4.6174650972581594e-04 beta[38] - 2.827963931321111e-04 beta[39]
   + 0.1027691228213636 beta[40] + 0.0337222800068193 beta[41]
   + 0.0131300734697332 beta[42] + 0.00578189393058902 beta[43]
   + 0.00282481331462258 beta[44] + 0.00151511840825104 beta[45]
   + 8.8284885188821447e-04 beta[46] + 5.5209812206601691e-04 beta[47]
   - 0.1588521872603374 beta[48] - 0.0414908510883204 beta[49]
   - 0.0143659981036078 beta[50] - 0.00593240380321276 beta[51]
   - 0.00282510803254777 beta[52] - 0.00152051251385759 beta[53]
   - 0.000905284 beta[54] - 5.8338939021803976e-04 beta[55]
   + 0.1250702706209529 beta[56] + 0.0272128952850616 beta[57]
   + 0.00838833 beta[58] + 0.00331281595070486 beta[59]
   + 0.00161269617582591 beta[60] + 9.2439780167491046e-04 beta[61]
   + 5.931006499687077e-04 beta[62] + 4.0961069126489356e-04 beta[63]
   - 0.0035592336614942 beta[64] + 0.00292741862549204 beta[65]
   + 0.00145491129674339 beta[66] + 4.9091229530903572e-04 beta[67]
   + 7.14816e-05 beta[68] - 8.42875e-05 beta[69]
   - 1.2877362595773819e-04 beta[70] - 1.3040064215962921e-04 beta[71]
   - 0.112489402812336 beta[72] - 0.0305459883583271 beta[73]
   - 0.00972877984442744 beta[74] - 0.00351786854620764 beta[75]
   - 0.00141249268169404 beta[76] - 6.1650869771561595e-04 beta[77]
   - 2.8618467110728274e-04 beta[78] - 0.000137662 beta[79]
   + 0.1413959180066668 beta[80] + 0.0377065835458046 beta[81]
   + 0.0117352586242664 beta[82] + 0.00431405040780185 beta[83]
   + 0.00185866184296171 beta[84] + 9.189121768031146e-04 beta[85]
   + 0.000506741 beta[86] + 3.0316680300589063e-04 beta[87]
   - 0.0824284523463413 beta[88] - 0.0214699255783928 beta[89]
   - 0.00678112138436958 beta[90] - 0.00271078811724742 beta[91]
   - 0.00133554 beta[92] - 0.000765335 beta[93]
   - 4.8322658114168811e-04 beta[94] - 3.2450729317666825e-04 beta[95]
   - 0.0095517681617651 beta[96] - 0.00333996050985911 beta[97]
   - 0.00132683041950529 beta[98] - 0.000547348 beta[99]
   - 0.000214581 beta[100] - 6.4617e-05 beta[101] + 3.63061e-06 beta[102]
   + 3.334e-05 beta[103] + 0.00143694322749072 beta[104]
   + 3.9350737769480856e-04 beta[105] + 7.83699e-05 beta[106]
   - 2.95172e-05 beta[107] - 6.57157e-05 beta[108] - 7.42834e-05 beta[109]
   - 7.18223e-05 beta[110] - 6.52658e-05 beta[111]
   + 0.00364925304701845 beta[112] + 0.00153673700248802 beta[113]
   + 7.6718576965974781e-04 beta[114] + 4.2554269644749559e-04 beta[115]
   + 2.5485253391874452e-04 beta[116] + 1.6209419581835767e-04 beta[117]
   + 1.0859082913991051e-04 beta[118] + 7.62801e-05 beta[119]
   - 0.00168968056618333 beta[120] - 8.2049375540565572e-04 beta[121]
   - 0.000446538 beta[122] - 2.5534022728577191e-04 beta[123]
   - 1.5037344601899629e-04 beta[124] - 9.08163e-05 beta[125]
   - 5.64291e-05 beta[126] - 3.63115e-05 beta[127]
   - 7.6763259622221849e-04 beta[128] - 3.2689578140174594e-04 beta[129]
   - 1.663931069863376e-04 beta[130] - 9.80193e-05 beta[131]
   - 6.40412e-05 beta[132] - 4.45178e-05 beta[133] - 3.21365e-05 beta[134]
   - 2.38007e-05 beta[135] + 5.0646051063203343e-04 beta[136]
   + 4.7381585326649689e-04 beta[137] + 3.4765819297368069e-04 beta[138]
   + 2.4108850594230618e-04 beta[139] + 1.6527869404206225e-04 beta[140]
   + 1.1408340495648641e-04 beta[141] + 8.00798e-05 beta[142]
   + 5.74889e-05 beta[143] - 7.6155514091727451e-04 beta[144]
   - 5.083904558662967e-04 beta[145] - 3.3573465858489573e-04 beta[146]
   - 2.2128648602633954e-04 beta[147] - 0.000148236 beta[148]
   - 1.0203011200777893e-04 beta[149] - 7.24907e-05 beta[150]
   - 5.32173e-05 beta[151] + 0.00179016528520121 beta[152]
   + 6.9012859077184716e-04 beta[153] + 3.0753480943487198e-04 beta[154]
   + 1.532836155512936e-04 beta[155] + 8.56447e-05 beta[156]
   + 5.37193e-05 beta[157] + 3.7379e-05 beta[158] + 2.82209e-05 beta[159]
   - 6.1750578073337017e-04 beta[160] - 0.000177006 beta[161]
   - 3.91841e-05 beta[162] + 8.85886e-08 beta[163] + 8.11506e-06 beta[164]
   + 6.96976e-06 beta[165] + 3.84549e-06 beta[166] + 9.45499e-07 beta[167]
   - 0.00169178970991928 beta[168] - 7.1436958450391637e-04 beta[169]
   - 3.4595721246896992e-04 beta[170] - 1.8254148477904757e-04 beta[171]
   - 1.0309068659047502e-04 beta[172] - 6.15162e-05 beta[173]
   - 3.83596e-05 beta[174] - 2.47693e-05 beta[175]
   + 0.00188801263283019 beta[176] + 8.5362053867526816e-04 beta[177]
   + 4.2164052013054913e-04 beta[178] + 2.2496789100484935e-04 beta[179]
   + 1.287362495765098e-04 beta[180] + 7.86135e-05 beta[181]
   + 5.0981e-05 beta[182] + 3.4899e-05 beta[183]
   - 5.6934915477051208e-04 beta[184] - 3.2040385220221079e-04 beta[185]
   - 1.8496082366722963e-04 beta[186] - 1.1329613885212388e-04 beta[187]
   - 7.36525e-05 beta[188] - 5.07919e-05 beta[189] - 3.69754e-05 beta[190]
   - 2.81688e-05 beta[191] - 0.022889505051034 beta[192]
   - 0.00538869975041792 beta[193] + 0.00958974626506675 beta[194]
   + 0.00780603428954485 beta[195] - 0.00310682772254298 beta[196]
   - 0.00716772704819192 beta[197] - 0.0013441208546274 beta[198]
   + 0.00423406097421501 beta[199] + 0.00904481275476884 beta[200]
   + 0.0023883889983759 beta[201] - 0.00381889780482627 beta[202]
   - 0.00381404367077908 beta[203] + 0.000598508 beta[204]
   + 0.00333166544322523 beta[205] + 0.00169849031261116 beta[206]
   - 0.00135172798525547 beta[207] + 0.00398383283072027 beta[208]
   + 8.5911121201006138e-04 beta[209] - 0.00136630613947411 beta[210]
   - 4.7244828481387776e-04 beta[211] + 0.00114162593051028 beta[212]
   + 5.879608985571652e-04 beta[213] - 0.00116013788272713 beta[214]
   - 0.00120775403583374 beta[215] - 0.00661719474165982 beta[216]
   - 0.00204592476865402 beta[217] + 0.00210217613765156 beta[218]
   + 0.00203729950040496 beta[219] - 6.0998441942576218e-04 beta[220]
   - 0.00172339488293215 beta[221] - 0.000220366 beta[222]
   + 0.00128725109074508 beta[223] + 0.00290636136609453 beta[224]
   + 0.0013804083892805 beta[225] - 5.0578719958382912e-04 beta[226]
   - 0.00128792318343446 beta[227] - 4.9342210353608073e-04 beta[228]
   + 0.000805302 beta[229] + 0.00106021756057976 beta[230]
   + 1.85711e-06 beta[231] + 8.44689e-06 beta[232]
   - 3.8232532538860374e-04 beta[233] - 3.5975437597946593e-04 beta[234]
   + 2.8072366668014385e-04 beta[235] + 6.1850740502100308e-04 beta[236]
   - 2.83268e-05 beta[237] - 8.6138445121909137e-04 beta[238]
   - 0.000584596 beta[239] - 5.8761867012177462e-04 beta[240]
   - 1.7161552670713097e-04 beta[241] + 0.000143438 beta[242]
   + 8.61763e-05 beta[243] - 3.83825e-05 beta[244] + 8.16613e-05 beta[245]
   + 2.5488787010547468e-04 beta[246] + 1.2845880816805301e-04 beta[247]
   + 6.8262982046357189e-04 beta[248] + 5.1292233779127582e-04 beta[249]
   + 1.3780570598701683e-04 beta[250] - 0.000302549 beta[251]
   - 4.5934487766487604e-04 beta[252] - 1.529775154834165e-04 beta[253]
   + 2.7389774119161275e-04 beta[254] + 2.8105124908361765e-04 beta[255]
   - 0.0014422528238067 beta[256] - 8.3132945478904085e-04 beta[257]
   + 9.65871e-05 beta[258] + 6.9617281410935187e-04 beta[259]
   + 0.000471578 beta[260] - 2.2998446961817635e-04 beta[261]
   - 0.000506688 beta[262] - 5.65259e-05 beta[263]
   + 0.00211992685238061 beta[264] + 0.000814972 beta[265]
   - 0.000542217 beta[266] - 7.9502915211921235e-04 beta[267]
   - 7.6424e-05 beta[268] + 5.1142739977112837e-04 beta[269]
   + 2.9774630430053095e-04 beta[270] - 2.5967549859422917e-04 beta[271]
   - 0.00104038084080958 beta[272] - 2.6545041727054123e-04 beta[273]
   + 3.4093541706876071e-04 beta[274] + 2.3351534023220848e-04 beta[275]
   - 1.2967140775075659e-04 beta[276] - 1.7448959226751151e-04 beta[277]
   + 8.3536e-06 beta[278] + 8.93356e-05 beta[279]
   - 0.0013770172195875 beta[280] - 3.9090114241152027e-04 beta[281]
   + 0.000505554 beta[282] + 4.8206080781025215e-04 beta[283]
   - 1.0593421576113919e-04 beta[284] - 3.4132927010652018e-04 beta[285]
   - 1.49992e-05 beta[286] + 2.2737166390041742e-04 beta[287]
   - 0.0775469772918346 beta[288] + 0.00276404449569422 beta[289]
   - 0.0201606148893171 beta[290] + weighted_residual[15]
   = -0.1160977672264934
 R606: - 0.1201372699334516 beta[0] - 0.0120351707424392 beta[1]
   + 0.000989359 beta[2] + 0.00294315013351484 beta[3]
   + 0.0028151222855147 beta[4] + 0.00229076969834062 beta[5]
   + 0.00177631789275683 beta[6] + 0.00136039785977511 beta[7]
   + 0.0457642841578326 beta[8] - 0.00591811800539991 beta[9]
   - 0.00759947655148731 beta[10] - 0.00566738948732721 beta[11]
   - 0.00399023428101095 beta[12] - 0.00281099360117511 beta[13]
   - 0.0020106163328082 beta[14] - 0.00146722646495362 beta[15]
   + 0.0199090233185133 beta[16] + 0.0259799620312007 beta[17]
   + 0.015424243273163 beta[18] + 0.00894224495278313 beta[19]
   + 0.00540998167216719 beta[20] + 0.00344058372320026 beta[21]
   + 0.00229428854296775 beta[22] + 0.00159655166958281 beta[23]
   - 0.0656044600702652 beta[24] - 0.0415218760199451 beta[25]
   - 0.0210962821022816 beta[26] - 0.0111662824427883 beta[27]
   - 0.00632472863857046 beta[28] - 0.003829343282771 beta[29]
   - 0.00246344188796251 beta[30] - 0.00167145587909239 beta[31]
   + 0.1244256749579018 beta[32] + 0.0560211239068543 beta[33]
   + 0.0252139809901422 beta[34] + 0.0124366199061506 beta[35]
   + 0.00673336864512378 beta[36] + 0.00396282944100839 beta[37]
   + 0.00250672769269098 beta[38] + 0.00168500411499484 beta[39]
   - 0.1813055242386027 beta[40] - 0.0690809524706294 beta[41]
   - 0.0285249873253251 beta[42] - 0.0132770100615366 beta[43]
   - 0.00692369366843324 beta[44] - 0.00398849417390251 beta[45]
   - 0.00249754421405337 beta[46] - 0.00167321965857997 beta[47]
   + 0.2259625974974956 beta[48] + 0.0794350287377676 beta[49]
   + 0.0309746642436175 beta[50] + 0.0138364142970018 beta[51]
   + 0.00702776416832771 beta[52] + 0.0039912569227397 beta[53]
   + 0.00248452716269478 beta[54] + 0.00166240896394732 beta[55]
   - 0.2751994719002157 beta[56] - 0.0889164832955463 beta[57]
   - 0.0328599651659385 beta[58] - 0.0141871088572751 beta[59]
   - 0.00707249414460689 beta[60] - 0.00398443436757777 beta[61]
   - 0.00247498431765639 beta[62] - 0.00165663906158103 beta[63]
   + 0.3226604113646799 beta[64] + 0.097466826871823 beta[65]
   + 0.034424162919734 beta[66] + 0.0144368394560265 beta[67]
   + 0.00709073420886102 beta[68] + 0.00397385045231582 beta[69]
   + 0.00246724740053617 beta[70] + 0.00165319056074978 beta[71]
   - 0.3611493284409818 beta[72] - 0.1043957711806622 beta[73]
   - 0.035632583945221 beta[74] - 0.0146153971847841 beta[75]
   - 0.00710074525457992 beta[76] - 0.00396586652712715 beta[77]
   - 0.00246219645777547 beta[78] - 0.00165121612691196 beta[79]
   + 0.4019218554145791 beta[80] + 0.1108596009637357 beta[81]
   + 0.0366234245402994 beta[82] + 0.0147393900633341 beta[83]
   + 0.00710367838726011 beta[84] + 0.0039599675511802 beta[85]
   + 0.00245934203565242 beta[86] + 0.00165037961710896 beta[87]
   - 0.4414756045663935 beta[88] - 0.116803285590682 beta[89]
   - 0.0374854462151656 beta[90] - 0.0148376256153258 beta[91]
   - 0.00710400367432633 beta[92] - 0.00395519583706649 beta[93]
   - 0.00245746789958145 beta[94] - 0.00165001143753666 beta[95]
   - 0.00692837630813633 beta[96] - 0.00164484887384637 beta[97]
   - 0.000731097 beta[98] - 0.000414853 beta[99]
   - 2.5514825215157492e-04 beta[100] - 1.6246752264969605e-04 beta[101]
   - 1.0549848334044624e-04 beta[102] - 6.93974e-05 beta[103]
   + 2.9190184324258026e-04 beta[104] + 0.00023316 beta[105]
   + 1.7454447251561157e-04 beta[106] + 1.2306622352370409e-04 beta[107]
   + 8.45526e-05 beta[108] + 5.75423e-05 beta[109] + 3.90596e-05 beta[110]
   + 2.65212e-05 beta[111] + 0.00120635137325824 beta[112]
   + 1.6668534912367167e-04 beta[113] + 6.93813e-05 beta[114]
   + 4.31939e-05 beta[115] + 2.85682e-05 beta[116] + 1.91553e-05 beta[117]
   + 1.29391e-05 beta[118] + 8.78622e-06 beta[119]
   + 0.0010441729451787 beta[120] + 2.2698934949501158e-04 beta[121]
   + 4.19877e-05 beta[122] - 5.65785e-06 beta[123] - 1.67695e-05 beta[124]
   - 1.70865e-05 beta[125] - 1.43912e-05 beta[126] - 1.12411e-05 beta[127]
   - 1.4026365852721668e-04 beta[128] - 3.23339e-05 beta[129]
   - 2.05736e-05 beta[130] - 9.24011e-06 beta[131] - 2.52468e-06 beta[132]
   + 6.16914e-07 beta[133] + 1.79768e-06 beta[134] + 2.03424e-06 beta[135]
   - 6.1904820553157925e-04 beta[136] - 1.223543088561111e-04 beta[137]
   - 4.01454e-05 beta[138] - 1.69557e-05 beta[139] - 7.50971e-06 beta[140]
   - 3.12045e-06 beta[141] - 1.04289e-06 beta[142] - 9.54584e-08 beta[143]
   - 5.0152466721052104e-04 beta[144] - 9.71442e-05 beta[145]
   - 1.1253e-05 beta[146] + 4.76305e-06 beta[147] + 5.78398e-06 beta[148]
   + 4.05806e-06 beta[149] + 2.35987e-06 beta[150] + 1.17892e-06 beta[151]
   + 9.84249e-05 beta[152] + 1.5013e-05 beta[153] + 7.31705e-06 beta[154]
   + 3.04651e-06 beta[155] + 8.53222e-07 beta[156] + 3.0743e-09 beta[157]
   - 2.22333e-07 beta[158] - 2.14862e-07 beta[159]
   + 4.2371915689581359e-04 beta[160] + 8.81874e-05 beta[161]
   + 2.4176e-05 beta[162] + 7.51233e-06 beta[163] + 2.1421e-06 beta[164]
   + 3.14434e-07 beta[165] - 2.45057e-07 beta[166] - 3.45482e-07 beta[167]
   + 3.1539367687154034e-04 beta[168] + 5.9509e-05 beta[169]
   + 7.16567e-06 beta[170] - 1.44751e-06 beta[171] - 1.76346e-06 beta[172]
   - 9.74519e-07 beta[173] - 3.7374e-07 beta[174] - 5.69596e-08 beta[175]
   - 8.60946e-05 beta[176] - 1.34472e-05 beta[177] - 5.18125e-06 beta[178]
   - 2.1854e-06 beta[179] - 8.14285e-07 beta[180] - 2.62961e-07 beta[181]
   - 7.14704e-08 beta[182] - 1.63646e-08 beta[183] - 0.000324264 beta[184]
   - 6.76519e-05 beta[185] - 1.6506e-05 beta[186] - 4.1793e-06 beta[187]
   - 8.40273e-07 beta[188] + 3.43187e-08 beta[189] + 1.93398e-07 beta[190]
   + 1.63072e-07 beta[191] - 0.024028871971514 beta[192]
   - 0.00514693569738866 beta[193] + 0.00952927062080682 beta[194]
   + 0.00617630450118443 beta[195] - 0.00378543424118744 beta[196]
   - 0.00473419303424788 beta[197] + 0.00120297413361864 beta[198]
   + 0.00279740484802142 beta[199] + 0.00490670547294603 beta[200]
   + 0.00207955388337115 beta[201] - 0.00113876972072795 beta[202]
   - 0.00222968598302221 beta[203] - 9.0033452258340692e-04 beta[204]
   + 9.5050688806703543e-04 beta[205] + 0.00140194970718615 beta[206]
   + 3.8364579936242245e-04 beta[207] + 0.00557313217701129 beta[208]
   + 4.2794753874159878e-04 beta[209] - 0.00283280670732157 beta[210]
   - 0.000707352 beta[211] + 0.00225875556413354 beta[212]
   + 0.00131844983126323 beta[213] - 0.00149794 beta[214]
   - 0.00167463047437111 beta[215] - 0.00140464021144621 beta[216]
   - 8.0284681525250208e-04 beta[217] + 1.5090137898449594e-04 beta[218]
   + 7.4120139565378527e-04 beta[219] + 3.627481813246766e-04 beta[220]
   - 5.1139885869420443e-04 beta[221] - 6.8625649236102055e-04 beta[222]
   + 0.000122687 beta[223] - 6.0556744175001016e-04 beta[224]
   + 0.000571632 beta[225] + 0.000907123 beta[226]
   - 2.6469659641226265e-04 beta[227] - 0.00111675376635223 beta[228]
   - 0.000284527 beta[229] + 9.6053443492744321e-04 beta[230]
   + 0.000770942 beta[231] - 0.00216380704610645 beta[232]
   - 0.000588074 beta[233] + 6.1698220166189538e-04 beta[234]
   + 4.1505055489441674e-04 beta[235] - 1.513316692983668e-04 beta[236]
   - 4.30122e-05 beta[237] + 0.000188822 beta[238] - 0.000197372 beta[239]
   + 0.00117615 beta[240] + 3.5519227148577212e-04 beta[241]
   - 0.000336991 beta[242] - 2.903961168055025e-04 beta[243]
   + 7.52436e-05 beta[244] + 1.2004767113918449e-04 beta[245]
   - 7.04282e-05 beta[246] - 1.35392e-05 beta[247]
   + 0.00119817928541485 beta[248] + 3.47843e-05 beta[249]
   - 6.2109168811589623e-04 beta[250] - 6.96802e-05 beta[251]
   + 4.8969416405904602e-04 beta[252] + 1.0847379929195453e-04 beta[253]
   - 4.3785114988465076e-04 beta[254] - 1.8972137318263397e-04 beta[255]
   - 2.201652467170692e-04 beta[256] - 1.5680728068628294e-04 beta[257]
   - 3.05594e-05 beta[258] + 8.52115e-05 beta[259] + 9.96832e-05 beta[260]
   + 3.58434e-05 beta[261] - 1.06789e-05 beta[262] - 2.38788e-05 beta[263]
   - 3.2588120411179944e-04 beta[264] + 2.1556683338431904e-04 beta[265]
   + 3.923616905326194e-04 beta[266] - 8.59273e-05 beta[267]
   - 4.3470934770387966e-04 beta[268] - 0.00012671 beta[269]
   + 0.000286868 beta[270] + 1.7971143854183451e-04 beta[271]
   - 0.00115243561847231 beta[272] - 3.4841124453680061e-04 beta[273]
   + 0.000319563 beta[274] + 2.7744441023847547e-04 beta[275]
   - 5.21793e-05 beta[276] - 9.37564e-05 beta[277] + 5.67037e-05 beta[278]
   + 2.67614e-05 beta[279] + 8.8161912772856106e-04 beta[280]
   + 0.000280529 beta[281] - 2.3975752483509013e-04 beta[282]
   - 0.000236345 beta[283] + 1.98225e-05 beta[284] + 9.84315e-05 beta[285]
   + 6.99097e-06 beta[286] - 1.46883e-05 beta[287]
   - 0.1178540361261741 beta[288] + 0.00309079183408369 beta[289]
   - 0.0255279227953956 beta[290] + weighted_residual[16]
   = -0.1574379255457141
 R607: - 0.0299961359451209 beta[0] - 0.00368607445197093 beta[1]
   - 0.00163126530578653 beta[2] - 7.2230752443037342e-04 beta[3]
   - 3.4643145694870334e-04 beta[4] - 1.8456284259250942e-04 beta[5]
   - 1.0770923067544695e-04 beta[6] - 6.75237e-05 beta[7]
   + 0.0299961359451211 beta[8] + 0.00368607445197094 beta[9]
   + 0.00163126530578653 beta[10] + 7.2230752443037418e-04 beta[11]
   + 3.4643145694870323e-04 beta[12] + 1.8456284259250931e-04 beta[13]
   + 1.0770923067544703e-04 beta[14] + 6.75237e-05 beta[15]
   - 0.029996135945121 beta[16] - 0.00368607445197093 beta[17]
   - 0.00163126530578653 beta[18] - 7.2230752443037461e-04 beta[19]
   - 3.4643145694870312e-04 beta[20] - 1.8456284259250918e-04 beta[21]
   - 1.07709230675447e-04 beta[22] - 6.75237e-05 beta[23]
   + 0.0299961359451209 beta[24] + 0.00368607445197094 beta[25]
   + 0.00163126530578653 beta[26] + 7.2230752443037342e-04 beta[27]
   + 3.4643145694870301e-04 beta[28] + 1.8456284259250931e-04 beta[29]
   + 1.077092306754471e-04 beta[30] + 6.75237e-05 beta[31]
   - 0.0299961359451209 beta[32] - 0.00368607445197093 beta[33]
   - 0.00163126530578653 beta[34] - 7.2230752443037342e-04 beta[35]
   - 3.4643145694870312e-04 beta[36] - 1.8456284259250948e-04 beta[37]
   - 1.077092306754471e-04 beta[38] - 6.75237e-05 beta[39]
   + 0.0299961359451208 beta[40] + 0.00368607445197094 beta[41]
   + 0.00163126530578653 beta[42] + 7.223075244303732e-04 beta[43]
   + 3.4643145694870334e-04 beta[44] + 1.8456284259250942e-04 beta[45]
   + 1.0770923067544707e-04 beta[46] + 6.75237e-05 beta[47]
   - 0.0299961359451209 beta[48] - 0.00368607445197096 beta[49]
   - 0.00163126530578653 beta[50] - 7.2230752443037363e-04 beta[51]
   - 3.4643145694870301e-04 beta[52] - 1.8456284259250918e-04 beta[53]
   - 1.07709230675447e-04 beta[54] - 6.75237e-05 beta[55]
   + 0.0299961359451209 beta[56] + 0.00368607445197097 beta[57]
   + 0.00163126530578653 beta[58] + 7.223075244303732e-04 beta[59]
   + 3.4643145694870323e-04 beta[60] + 1.8456284259250918e-04 beta[61]
   + 1.0770923067544705e-04 beta[62] + 6.75237e-05 beta[63]
   - 0.0299961359451208 beta[64] - 0.00368607445197097 beta[65]
   - 0.00163126530578653 beta[66] - 7.2230752443037298e-04 beta[67]
   - 3.4643145694870339e-04 beta[68] - 1.8456284259250931e-04 beta[69]
   - 1.077092306754471e-04 beta[70] - 6.75237e-05 beta[71]
   + 0.0299961359451209 beta[72] + 0.00368607445197098 beta[73]
   + 0.00163126530578653 beta[74] + 7.2230752443037342e-04 beta[75]
   + 3.4643145694870312e-04 beta[76] + 1.8456284259250937e-04 beta[77]
   + 1.077092306754471e-04 beta[78] + 6.75237e-05 beta[79]
   - 0.0299961359451209 beta[80] - 0.00368607445197096 beta[81]
   - 0.00163126530578652 beta[82] - 7.2230752443037222e-04 beta[83]
   - 3.4643145694870274e-04 beta[84] - 1.8456284259250937e-04 beta[85]
   - 1.077092306754471e-04 beta[86] - 6.75237e-05 beta[87]
   + 0.0299961359451208 beta[88] + 0.00368607445197097 beta[89]
   + 0.00163126530578653 beta[90] + 7.2230752443037212e-04 beta[91]
   + 3.4643145694870323e-04 beta[92] + 1.845628425925095e-04 beta[93]
   + 1.0770923067544705e-04 beta[94] + 6.75237e-05 beta[95]
   - 0.0321885369996884 beta[192] - 0.00736664864236893 beta[193]
   + 0.0121227390813676 beta[194] + 0.00787065543229046 beta[195]
   - 0.00536784780921333 beta[196] - 0.00648637582116445 beta[197]
   + 0.00225592431932683 beta[198] + 0.00509914912097744 beta[199]
   + 3.9231239592620758e-04 beta[200] + 0.00236862071734762 beta[201]
   + 0.00191035038196209 beta[202] - 0.00142976326345391 beta[203]
   - 0.00268496695657957 beta[204] + 8.76291e-05 beta[205]
   + 0.00232147233670146 beta[206] + 6.0937477518092681e-04 beta[207]
   + 0.00674782668869024 beta[208] + 9.2263982788134556e-04 beta[209]
   - 0.00366552955716786 beta[210] - 0.00222507367780932 beta[211]
   + 0.00192818171433234 beta[212] + 0.00269739966698022 beta[213]
   - 3.4705142692039364e-04 beta[214] - 0.00227865875066049 beta[215]
   - 4.5253688975904185e-04 beta[216] - 7.7514535066362388e-04 beta[217]
   - 1.1158915173439868e-04 beta[218] + 0.0012096743581538 beta[219]
   + 0.00111000893241173 beta[220] - 6.8616944300202301e-04 beta[221]
   - 0.00162617282949014 beta[222] - 2.1500014018270249e-04 beta[223]
   - 9.8165679200970394e-04 beta[224] + 6.01579e-05 beta[225]
   + 0.000746183 beta[226] + 1.1934260192209491e-04 beta[227]
   - 9.4911337683916514e-04 beta[228] - 0.000823573 beta[229]
   + 5.2806619214061038e-04 beta[230] + 0.00125427753632604 beta[231]
   + 2.0765242320146881e-04 beta[232] - 4.09651e-07 beta[233]
   - 2.4446848401662232e-04 beta[234] - 2.1915747391569671e-04 beta[235]
   + 1.9442048877274507e-04 beta[236] + 5.8789624675326699e-04 beta[237]
   + 3.5597582244356179e-04 beta[238] - 4.1547153452024788e-04 beta[239]
   + 5.8899642607567859e-04 beta[240] + 1.2179361173543317e-04 beta[241]
   - 1.7757052379358492e-04 beta[242] - 2.99719e-06 beta[243]
   + 1.8190779507724019e-04 beta[244] - 8.42046e-05 beta[245]
   - 4.6513174524262388e-04 beta[246] - 2.8528585347616494e-04 beta[247]
   - 4.81292e-05 beta[248] - 8.25642e-05 beta[249] - 6.43165e-05 beta[250]
   - 9.53428e-06 beta[251] - 8.43129e-06 beta[252] - 4.55373e-06 beta[253]
   + 1.3479458792126024e-04 beta[254] + 2.8572927352272826e-04 beta[255]
   - 0.000136787 beta[256] + 3.65277e-06 beta[257]
   + 1.1328116547525915e-04 beta[258] + 8.14e-05 beta[259]
   - 9.20259e-06 beta[260] - 3.7274e-05 beta[261] - 3.91437e-05 beta[262]
   - 1.1618962249581661e-04 beta[263] + 2.58128e-06 beta[264]
   + 1.5286e-06 beta[265] - 2.1921e-05 beta[266] - 5.38801e-05 beta[267]
   - 5.05237e-05 beta[268] - 7.64213e-06 beta[269] + 3.63335e-05 beta[270]
   + 7.29128e-05 beta[271] + 5.00313e-05 beta[272] + 1.40194e-05 beta[273]
   - 1.03129e-05 beta[274] + 9.67918e-06 beta[275] + 4.72296e-05 beta[276]
   + 4.9594e-05 beta[277] + 4.18162e-06 beta[278] - 5.38429e-05 beta[279]
   - 2.23391e-05 beta[280] - 1.07976e-05 beta[281] + 1.3292e-06 beta[282]
   - 1.91865e-06 beta[283] - 2.37488e-05 beta[284] - 4.25286e-05 beta[285]
   - 3.06295e-05 beta[286] + 1.27825e-05 beta[287]
   - 0.0363689179480715 beta[288] - 3.79118e-05 beta[289]
   - 0.0344420572097808 beta[290] + weighted_residual[17]
   = -0.0705225901836497
 R608: - 0.0282117383349266 beta[0] + 0.0122524513594828 beta[1]
   + 0.0074428109968898 beta[2] + 0.00337934262872607 beta[3]
   + 0.00155401396672602 beta[4] + 0.000768238 beta[5]
   + 4.131481060229065e-04 beta[6] + 2.4079179775067169e-04 beta[7]
   - 0.0760821470055402 beta[8] - 0.0167479205768933 beta[9]
   - 0.00494433749314739 beta[10] - 0.00173120511744118 beta[11]
   - 7.0534471225777392e-04 beta[12] - 3.3031728647711791e-04 beta[13]
   - 0.000174706 beta[14] - 0.000102241 beta[15]
   + 0.0685328421239323 beta[16] + 0.00704537588173812 beta[17]
   + 7.64931e-05 beta[18] - 0.000385192 beta[19]
   - 2.476146047505263e-04 beta[20] - 1.3425936870863561e-04 beta[21]
   - 7.25851e-05 beta[22] - 4.07688e-05 beta[23]
   + 0.0640362776214573 beta[24] + 0.0137630237806352 beta[25]
   + 0.00409738793815443 beta[26] + 0.00140699198305866 beta[27]
   + 5.5126055478311314e-04 beta[28] + 2.4669850133780336e-04 beta[29]
   + 0.000125279 beta[30] + 7.11405e-05 beta[31]
   - 0.1028028482547826 beta[32] - 0.0178583845875082 beta[33]
   - 0.00340190018053903 beta[34] - 0.000699044 beta[35]
   - 1.4338456181447852e-04 beta[36] - 2.56907e-05 beta[37]
   - 2.75788e-06 beta[38] - 1.48274e-07 beta[39]
   - 0.00935174779815712 beta[40] - 0.00231240137481224 beta[41]
   - 0.00140570861735928 beta[42] - 0.000716896 beta[43]
   - 3.6725775030327173e-04 beta[44] - 1.9936119010434519e-04 beta[45]
   - 1.156046161961077e-04 beta[46] - 7.11468e-05 beta[47]
   + 0.0914208405305115 beta[48] + 0.0186501197766743 beta[49]
   + 0.0042121620403768 beta[50] + 0.00111787489719796 beta[51]
   + 3.7060655959269531e-04 beta[52] + 1.6306669548695848e-04 beta[53]
   + 9.29575e-05 beta[54] + 6.25938e-05 beta[55]
   - 0.0420239567500297 beta[56] - 0.00900831839604137 beta[57]
   - 0.00132313188405424 beta[58] - 2.61216e-05 beta[59]
   + 0.000115177 beta[60] + 8.12274e-05 beta[61] + 4.15372e-05 beta[62]
   + 1.65724e-05 beta[63] - 0.041738204431407 beta[64]
   - 0.01147758429528 beta[65] - 0.00332796579578715 beta[66]
   - 0.00116175289937394 beta[67] - 4.9484520091658366e-04 beta[68]
   - 2.48268380742452e-04 beta[69] - 1.3918767305224272e-04 beta[70]
   - 8.36319e-05 beta[71] + 0.0572901557547342 beta[72]
   + 0.0150841942843331 beta[73] + 0.00349296666131358 beta[74]
   + 8.917397912507997e-04 beta[75] + 0.000295673 beta[76]
   + 1.4355518462673411e-04 beta[77] + 9.25681e-05 beta[78]
   + 6.72901e-05 beta[79] - 0.0143406674009375 beta[80]
   + 3.3943225875865293e-04 beta[81] + 9.0649585598556064e-04 beta[82]
   + 5.2066685323704247e-04 beta[83] + 2.5043823563753858e-04 beta[84]
   + 0.00011024 beta[85] + 4.28162e-05 beta[86] + 1.15968e-05 beta[87]
   - 0.0306361737531412 beta[88] - 0.0131524715779039 beta[89]
   - 0.00392999038022841 beta[90] - 0.00125113263279789 beta[91]
   - 4.6906387580451938e-04 beta[92] - 2.1075880738425403e-04 beta[93]
   - 0.000108651 beta[94] - 6.07688e-05 beta[95]
   - 0.0134229742996163 beta[96] - 0.0020391793626769 beta[97]
   - 3.21755e-05 beta[98] + 3.1254842563592923e-04 beta[99]
   + 3.2626461562019099e-04 beta[100] + 0.000278393 beta[101]
   + 2.2731948667470967e-04 beta[102] + 1.8458837904195845e-04 beta[103]
   - 0.00391089865345172 beta[104] - 0.00128806912000238 beta[105]
   - 6.191885936151231e-04 beta[106] - 3.4489114751077551e-04 beta[107]
   - 0.000211421 beta[108] - 1.4001237791996302e-04 beta[109]
   - 9.88695e-05 beta[110] - 7.35932e-05 beta[111]
   + 0.008704826226216 beta[112] + 0.00209328406380405 beta[113]
   + 5.6632116895621442e-04 beta[114] + 0.000141119 beta[115]
   + 8.07089e-06 beta[116] - 3.41868e-05 beta[117] - 4.51976e-05 beta[118]
   - 4.5035e-05 beta[119] + 0.00352614216136454 beta[120]
   + 8.8816127291137053e-04 beta[121] + 3.9674160546261959e-04 beta[122]
   + 0.000227145 beta[123] + 1.5035780149116041e-04 beta[124]
   + 1.0971756340196434e-04 beta[125] + 8.54602e-05 beta[126]
   + 6.95001e-05 beta[127] - 0.00797320392942996 beta[128]
   - 0.00239798954370023 beta[129] - 0.000817456 beta[130]
   - 0.000299482 beta[131] - 1.1035479458777319e-04 beta[132]
   - 3.75739e-05 beta[133] - 9.63216e-06 beta[134] + 2.32756e-07 beta[135]
   - 0.00141540658626769 beta[136] + 4.48181e-05 beta[137]
   + 1.16796e-05 beta[138] - 5.11128e-05 beta[139] - 7.79793e-05 beta[140]
   - 8.32302e-05 beta[141] - 7.85901e-05 beta[142] - 7.02431e-05 beta[143]
   + 0.00629076113873561 beta[144] + 0.00209067169439979 beta[145]
   + 7.708078097048008e-04 beta[146] + 3.2773541777185954e-04 beta[147]
   + 1.6449264126193014e-04 beta[148] + 9.93584e-05 beta[149]
   + 7.10281e-05 beta[150] + 5.71744e-05 beta[151]
   - 6.3471248482601013e-04 beta[152] - 8.444144418056611e-04 beta[153]
   - 3.6101832358734784e-04 beta[154] - 1.1705431085678975e-04 beta[155]
   - 1.67076e-05 beta[156] + 1.83419e-05 beta[157] + 2.61026e-05 beta[158]
   + 2.34845e-05 beta[159] - 0.00379634303842381 beta[160]
   - 0.00137303134608163 beta[161] - 5.5512640995433727e-04 beta[162]
   - 2.8304362508336205e-04 beta[163] - 0.000178299 beta[164]
   - 1.2883982864389716e-04 beta[165] - 9.99071e-05 beta[166]
   - 7.9982e-05 beta[167] + 0.00174193466607476 beta[168]
   + 0.00129760166023697 beta[169] + 6.2708051216106716e-04 beta[170]
   + 2.9853145898847401e-04 beta[171] + 0.000153718 beta[172]
   + 9.12117e-05 beta[173] + 6.37716e-05 beta[174] + 5.08864e-05 beta[175]
   + 0.0012531416730641 beta[176] + 4.2247383089665067e-04 beta[177]
   + 1.5277678967426451e-04 beta[178] + 8.87598e-05 beta[179]
   + 6.71565e-05 beta[180] + 5.19626e-05 beta[181] + 3.81056e-05 beta[182]
   + 2.59256e-05 beta[183] - 0.00159529031761149 beta[184]
   - 0.00119854761764036 beta[185] - 6.3652187464619859e-04 beta[186]
   - 3.3948415504317798e-04 beta[187] - 1.9516057406527231e-04 beta[188]
   - 1.2310457432652955e-04 beta[189] - 8.42856e-05 beta[190]
   - 6.1203e-05 beta[191] - 0.01839875509925 beta[192]
   + 0.00284998227558552 beta[193] + 0.0147016307751734 beta[194]
   + 0.00217480401685513 beta[195] - 0.0130169287467503 beta[196]
   - 0.00753321438179566 beta[197] + 0.00865411825971314 beta[198]
   + 0.010268663498001 beta[199] + 0.00790875204305425 beta[200]
   - 0.00225371332908333 beta[201] - 0.00760113454010522 beta[202]
   - 9.8873975411209025e-04 beta[203] + 0.00668883305816008 beta[204]
   + 0.00393561030556389 beta[205] - 0.00420363053827751 beta[206]
   - 0.00516126720951797 beta[207] + 0.00479521630520139 beta[208]
   + 0.000972838 beta[209] - 0.00157302603273359 beta[210]
   - 2.4714138810170581e-04 beta[211] + 0.00165078090292576 beta[212]
   + 0.000633151 beta[213] - 0.00158743947976121 beta[214]
   - 0.00133520365218562 beta[215] - 0.00898301341281897 beta[216]
   + 8.2980112230627721e-04 beta[217] + 0.00614883315033749 beta[218]
   + 3.2995480864396633e-04 beta[219] - 0.00619269500677385 beta[220]
   - 0.00300026484968265 beta[221] + 0.00449697290930152 beta[222]
   + 0.00467665972044536 beta[223] + 0.00143367321159138 beta[224]
   - 0.00236493783519534 beta[225] - 0.00345725121234238 beta[226]
   + 6.7194649361875642e-04 beta[227] + 0.00428355479758664 beta[228]
   + 0.00211472493811202 beta[229] - 0.0026159460926912 beta[230]
   - 0.00319445866285704 beta[231] + 0.00838499916310787 beta[232]
   + 0.00248977729811044 beta[233] - 0.00205823948143473 beta[234]
   - 0.00129338748096231 beta[235] + 8.7548946515468855e-04 beta[236]
   + 1.7098423312511877e-04 beta[237] - 0.00154695463682983 beta[238]
   - 0.0006845 beta[239] - 0.00808009385972565 beta[240]
   - 8.0419252707619282e-04 beta[241] + 0.00359811321222081 beta[242]
   + 3.0032514249283095e-04 beta[243] - 0.00363409471783356 beta[244]
   - 0.00123173338916818 beta[245] + 0.00359779579252079 beta[246]
   + 0.00308231472664378 beta[247] - 0.00191482590826871 beta[248]
   - 0.0015664021456374 beta[249] - 2.4308423518438346e-04 beta[250]
   + 0.00167493525342822 beta[251] + 0.00229978278075742 beta[252]
   + 4.2681535285141571e-04 beta[253] - 0.00220375224643554 beta[254]
   - 0.00240851686588412 beta[255] + 0.0093612142671322 beta[256]
   + 0.00272946931450805 beta[257] - 0.00286365099704129 beta[258]
   - 0.00264001025437994 beta[259] + 9.21647e-05 beta[260]
   + 6.6123539315871168e-04 beta[261] - 0.000260986 beta[262]
   + 2.0879650764233591e-04 beta[263] - 0.00684709540368071 beta[264]
   - 0.00175760092647866 beta[265] + 0.00223038770425645 beta[266]
   + 0.00141673668381698 beta[267] - 9.2871373776226226e-04 beta[268]
   - 4.4982329241079975e-04 beta[269] + 0.0016300980418303 beta[270]
   + 0.00118274577553189 beta[271] - 0.00135600205273544 beta[272]
   - 0.000456994 beta[273] + 6.2813944270438628e-04 beta[274]
   + 0.00107096752877784 beta[275] + 4.646656958973126e-04 beta[276]
   - 8.6292969664066108e-04 beta[277] - 0.00175196677178464 beta[278]
   - 0.00100382109858273 beta[279] + 0.00750698291181858 beta[280]
   + 0.00205949689152008 beta[281] - 0.00278392372279715 beta[282]
   - 0.00270659871711583 beta[283] + 2.3682867324276282e-04 beta[284]
   + 0.00174716660606074 beta[285] + 0.00103148539420904 beta[286]
   + 1.9802680314447241e-04 beta[287] + 0.00437351911007879 beta[288]
   - 0.00219178370344996 beta[289] - 0.0689047937516384 beta[290]
   + weighted_residual[18] = -0.0510423016744403
 R609: - 0.0306069726748393 beta[0] + 0.0192338443281846 beta[1]
   + 0.00915635861249095 beta[2] + 0.00344956098618859 beta[3]
   + 0.00136731403083838 beta[4] + 0.000607509 beta[5]
   + 3.0483539398973151e-04 beta[6] + 0.000170299 beta[7]
   - 0.1142897528577104 beta[8] - 0.0201141174244477 beta[9]
   - 0.00507661787878295 beta[10] - 0.00156143780849108 beta[11]
   - 5.7410731913741444e-04 beta[12] - 2.4797072048543225e-04 beta[13]
   - 1.2250452591458343e-04 beta[14] - 6.72089e-05 beta[15]
   + 0.0947100377835266 beta[16] + 0.00489095552639763 beta[17]
   - 0.0010534504216664 beta[18] - 6.5198622462483936e-04 beta[19]
   - 2.8702984336666682e-04 beta[20] - 1.3227416960480244e-04 beta[21]
   - 6.91425e-05 beta[22] - 4.13174e-05 beta[23]
   + 0.1081437092493478 beta[24] + 0.0188380194744414 beta[25]
   + 0.00477569813757139 beta[26] + 0.00142353015272572 beta[27]
   + 5.0102440977718742e-04 beta[28] + 2.1055733432702366e-04 beta[29]
   + 1.0494059045128161e-04 beta[30] + 6.04793e-05 beta[31]
   - 0.1593025929667949 beta[32] - 0.0194673214976296 beta[33]
   - 0.00273299966906963 beta[34] - 4.3303354596357268e-04 beta[35]
   - 6.80806e-05 beta[36] - 4.10298e-06 beta[37] + 6.65609e-06 beta[38]
   + 7.26009e-06 beta[39] - 0.0361391436040744 beta[40]
   - 0.00701560901066327 beta[41] - 0.0024147354836022 beta[42]
   - 8.7164476921953462e-04 beta[43] - 3.6477184998305823e-04 beta[44]
   - 1.8353734477651994e-04 beta[45] - 1.0842943151338353e-04 beta[46]
   - 7.18551e-05 beta[47] + 0.1679044591940752 beta[48]
   + 0.0235886163375068 beta[49] + 0.00405774705116545 beta[50]
   + 0.000873916 beta[51] + 2.609696635620187e-04 beta[52]
   + 1.1785389993302668e-04 beta[53] + 7.39123e-05 beta[54]
   + 5.47667e-05 beta[55] - 0.0474757820533561 beta[56]
   - 0.00648394888409038 beta[57] - 1.0388124364450463e-04 beta[58]
   + 0.000333376 beta[59] + 2.1516383479461783e-04 beta[60]
   + 0.000115414 beta[61] + 5.97841e-05 beta[62] + 3.02754e-05 beta[63]
   - 0.1171739101402781 beta[64] - 0.0186061134993445 beta[65]
   - 0.00389991511235815 beta[66] - 0.00111238865519182 beta[67]
   - 4.4804270939507979e-04 beta[68] - 2.3608334214462429e-04 beta[69]
   - 1.4535375805198206e-04 beta[70] - 9.72425e-05 beta[71]
   + 0.0959440982541506 beta[72] + 0.0160021022215368 beta[73]
   + 0.00238779335359313 beta[74] + 4.1596340340154295e-04 beta[75]
   + 1.440345757789553e-04 beta[76] + 1.058938038266065e-04 beta[77]
   + 9.284e-05 beta[78] + 8.02141e-05 beta[79]
   + 0.0385262181631131 beta[80] + 0.00808110030077543 beta[81]
   + 0.0024106540626531 beta[82] + 8.3718934022733633e-04 beta[83]
   + 0.00032066 beta[84] + 0.000123073 beta[85] + 3.96008e-05 beta[86]
   + 2.79857e-06 beta[87] - 0.0905241518332383 beta[88]
   - 0.0185824011507462 beta[89] - 0.00377078794816275 beta[90]
   - 0.00100226342516137 beta[91] - 3.9253673109503593e-04 beta[92]
   - 2.0488735108064809e-04 beta[93] - 1.2182612375009235e-04 beta[94]
   - 7.59741e-05 beta[95] - 0.0168131195840609 beta[96]
   - 0.00157677443916166 beta[97] + 5.4550088285728454e-04 beta[98]
   + 6.5608065248316685e-04 beta[99] + 5.0107115116085257e-04 beta[100]
   + 3.5895516063295702e-04 beta[101] + 2.5893274024842025e-04 beta[102]
   + 1.9164860437897386e-04 beta[103] - 0.00477392244817723 beta[104]
   - 0.00157462219868319 beta[105] - 7.6337723510975218e-04 beta[106]
   - 4.2037868578762846e-04 beta[107] - 0.000252458 beta[108]
   - 1.6314831652092368e-04 beta[109] - 1.1225913895703588e-04 beta[110]
   - 8.14185e-05 beta[111] + 0.0114284186803842 beta[112]
   + 0.00207513799539505 beta[113] + 0.000344339 beta[114]
   + 1.42391e-06 beta[115] - 5.70868e-05 beta[116] - 5.62539e-05 beta[117]
   - 4.54681e-05 beta[118] - 3.52929e-05 beta[119]
   + 0.00437670863361584 beta[120] + 0.00122440338229712 beta[121]
   + 5.8480530132524187e-04 beta[122] + 3.1986640424969142e-04 beta[123]
   + 1.8986445681086183e-04 beta[124] + 0.000121263 beta[125]
   + 8.27782e-05 beta[126] + 5.98647e-05 beta[127]
   - 0.0114755437749891 beta[128] - 0.00272199349236545 beta[129]
   - 0.000758018 beta[130] - 2.3199375856393652e-04 beta[131]
   - 7.29647e-05 beta[132] - 2.11123e-05 beta[133] - 3.76458e-06 beta[134]
   + 1.69944e-06 beta[135] - 0.00154153618389729 beta[136]
   - 1.3337151394306792e-04 beta[137] - 1.4904246810048627e-04 beta[138]
   - 1.3630289414942785e-04 beta[139] - 1.1017326385562672e-04 beta[140]
   - 8.68447e-05 beta[141] - 6.88824e-05 beta[142] - 5.54283e-05 beta[143]
   + 0.0102148243001975 beta[144] + 0.00260376308890753 beta[145]
   + 7.8775013464410482e-04 beta[146] + 2.7554357489278323e-04 beta[147]
   + 1.1418745945579773e-04 beta[148] + 5.89017e-05 beta[149]
   + 3.83739e-05 beta[150] + 2.99022e-05 beta[151]
   - 0.00149433937464077 beta[152] - 0.000862478 beta[153]
   - 1.9341042233410471e-04 beta[154] + 1.68642e-05 beta[155]
   + 6.7055e-05 beta[156] + 6.86569e-05 beta[157] + 5.76503e-05 beta[158]
   + 4.51537e-05 beta[159] - 0.00742747303340627 beta[160]
   - 0.00199172188063756 beta[161] - 6.9117611833668534e-04 beta[162]
   - 3.1405856206252953e-04 beta[163] - 0.000183691 beta[164]
   - 0.000128093 beta[165] - 9.83416e-05 beta[166] - 7.91255e-05 beta[167]
   + 0.00346117852701922 beta[168] + 0.00155328465372689 beta[169]
   + 5.0777328888682624e-04 beta[170] + 0.000163027 beta[171]
   + 5.98975e-05 beta[172] + 3.30003e-05 beta[173] + 2.83957e-05 beta[174]
   + 2.91145e-05 beta[175] + 0.00394477507764526 beta[176]
   + 0.00107161674561922 beta[177] + 4.3663228438766598e-04 beta[178]
   + 2.4225950882871561e-04 beta[179] + 1.5737441770338238e-04 beta[180]
   + 1.0785071407390594e-04 beta[181] + 7.44961e-05 beta[182]
   + 5.0853e-05 beta[183] - 0.00389896515571766 beta[184]
   - 0.00181083192160101 beta[185] - 7.248916863995267e-04 beta[186]
   - 3.3037968270512133e-04 beta[187] - 1.8523229838073591e-04 beta[188]
   - 1.2488178034028151e-04 beta[189] - 9.41724e-05 beta[190]
   - 7.48413e-05 beta[191] - 0.0179547876082887 beta[192]
   + 0.00420198557714228 beta[193] + 0.0144710436344268 beta[194]
   - 8.164846636285149e-04 beta[195] - 0.0145791127468003 beta[196]
   - 0.00430320570269847 beta[197] + 0.0123112139584187 beta[198]
   + 0.0082030987865724 beta[199] + 0.00606745248159453 beta[200]
   - 0.00309782 beta[201] - 0.00663409429407992 beta[202]
   + 8.7587925270430126e-04 beta[203] + 0.00697050537647413 beta[204]
   + 0.00197762424809443 beta[205] - 0.00562204471651407 beta[206]
   - 0.00373204077056851 beta[207] + 0.00827640132773772 beta[208]
   + 0.00120612958848157 beta[209] - 0.0032541346026408 beta[210]
   - 5.4676481280471301e-04 beta[211] + 0.002792129749896 beta[212]
   + 7.0734838496942949e-04 beta[213] - 0.00288084128217252 beta[214]
   - 0.00161556109327704 beta[215] - 0.0107598849336465 beta[216]
   + 8.9165286252245997e-04 beta[217] + 0.00662565 beta[218]
   - 5.3099110538802358e-04 beta[219] - 0.0068697036649156 beta[220]
   - 0.00150462865253576 beta[221] + 0.00630220093276008 beta[222]
   + 0.00366254388463129 beta[223] - 0.00179521218136646 beta[224]
   - 0.00225088917983204 beta[225] - 0.00101949770943486 beta[226]
   + 0.00172242735541625 beta[227] + 0.00264399553613344 beta[228]
   + 2.3580761147055416e-04 beta[229] - 0.00233481856168534 beta[230]
   - 0.00157384879746227 beta[231] + 0.0126560032623869 beta[232]
   + 0.00192038664853022 beta[233] - 0.0051060683454893 beta[234]
   - 0.00156158109871503 beta[235] + 0.00326386242154306 beta[236]
   + 9.0385823121208074e-04 beta[237] - 0.0033126363498788 beta[238]
   - 0.0014169816755072 beta[239] - 0.00626795054412646 beta[240]
   - 5.85349e-05 beta[241] + 0.00312659640889335 beta[242]
   - 0.000367133 beta[243] - 0.00332733624514973 beta[244]
   - 1.6078433650030049e-04 beta[245] + 0.00391660568353709 beta[246]
   + 0.00192489151153715 beta[247] - 0.00792584235946341 beta[248]
   - 0.0016673722213698 beta[249] + 0.00319843818113667 beta[250]
   + 0.00228458721301672 beta[251] - 7.3576012361000333e-04 beta[252]
   - 0.00138097663384687 beta[253] - 4.3120587944093733e-04 beta[254]
   - 0.000247019 beta[255] + 0.0102620987485444 beta[256]
   + 0.00161613809320877 beta[257] - 0.00446166888863282 beta[258]
   - 0.00206049514381603 beta[259] + 0.00224087230388657 beta[260]
   + 0.00138183157859679 beta[261] - 0.00165758130896728 beta[262]
   - 8.4219754219297057e-04 beta[263] - 3.5460232326102459e-04 beta[264]
   - 1.03569e-05 beta[265] + 1.4562770125896456e-04 beta[266]
   - 1.1755268909723192e-04 beta[267] - 1.9777673459394357e-04 beta[268]
   + 0.000443149 beta[269] + 9.9027282377083122e-04 beta[270]
   + 1.1999016492995543e-04 beta[271] - 0.00737565517196632 beta[272]
   - 0.00136659030718356 beta[273] + 0.00322341131189831 beta[274]
   + 0.00193936695081305 beta[275] - 0.00151852479041679 beta[276]
   - 0.00200531 beta[277] - 1.35022e-05 beta[278] + 0.000954046 beta[279]
   + 0.00627297793288533 beta[280] + 0.00119836274846634 beta[281]
   - 0.0027307311390917 beta[282] - 0.00167231359315662 beta[283]
   + 0.00127119310448586 beta[284] + 0.00157873847408843 beta[285]
   - 0.00022941 beta[286] - 0.000711968 beta[287]
   + 0.0134760745568541 beta[288] - 0.00277728658388678 beta[289]
   - 0.0990824836752071 beta[290] + weighted_residual[19]
   = -0.0530100517393158
Bounds
 -25 <= beta[0] <= 25
 -25 <= beta[1] <= 25
 -25 <= beta[2] <= 25
 -25 <= beta[3] <= 25
 -25 <= beta[4] <= 25
 -25 <= beta[5] <= 25
 -25 <= beta[6] <= 25
 -25 <= beta[7] <= 25
 -25 <= beta[8] <= 25
 -25 <= beta[9] <= 25
 -25 <= beta[10] <= 25
 -25 <= beta[11] <= 25
 -25 <= beta[12] <= 25
 -25 <= beta[13] <= 25
 -25 <= beta[14] <= 25
 -25 <= beta[15] <= 25
 -25 <= beta[16] <= 25
 -25 <= beta[17] <= 25
 -25 <= beta[18] <= 25
 -25 <= beta[19] <= 25
 -25 <= beta[20] <= 25
 -25 <= beta[21] <= 25
 -25 <= beta[22] <= 25
 -25 <= beta[23] <= 25
 -25 <= beta[24] <= 25
 -25 <= beta[25] <= 25
 -25 <= beta[26] <= 25
 -25 <= beta[27] <= 25
 -25 <= beta[28] <= 25
 -25 <= beta[29] <= 25
 -25 <= beta[30] <= 25
 -25 <= beta[31] <= 25
 -25 <= beta[32] <= 25
 -25 <= beta[33] <= 25
 -25 <= beta[34] <= 25
 -25 <= beta[35] <= 25
 -25 <= beta[36] <= 25
 -25 <= beta[37] <= 25
 -25 <= beta[38] <= 25
 -25 <= beta[39] <= 25
 -25 <= beta[40] <= 25
 -25 <= beta[41] <= 25
 -25 <= beta[42] <= 25
 -25 <= beta[43] <= 25
 -25 <= beta[44] <= 25
 -25 <= beta[45] <= 25
 -25 <= beta[46] <= 25
 -25 <= beta[47] <= 25
 -25 <= beta[48] <= 25
 -25 <= beta[49] <= 25
 -25 <= beta[50] <= 25
 -25 <= beta[51] <= 25
 -25 <= beta[52] <= 25
 -25 <= beta[53] <= 25
 -25 <= beta[54] <= 25
 -25 <= beta[55] <= 25
 -25 <= beta[56] <= 25
 -25 <= beta[57] <= 25
 -25 <= beta[58] <= 25
 -25 <= beta[59] <= 25
 -25 <= beta[60] <= 25
 -25 <= beta[61] <= 25
 -25 <= beta[62] <= 25
 -25 <= beta[63] <= 25
 -25 <= beta[64] <= 25
 -25 <= beta[65] <= 25
 -25 <= beta[66] <= 25
 -25 <= beta[67] <= 25
 -25 <= beta[68] <= 25
 -25 <= beta[69] <= 25
 -25 <= beta[70] <= 25
 -25 <= beta[71] <= 25
 -25 <= beta[72] <= 25
 -25 <= beta[73] <= 25
 -25 <= beta[74] <= 25
 -25 <= beta[75] <= 25
 -25 <= beta[76] <= 25
 -25 <= beta[77] <= 25
 -25 <= beta[78] <= 25
 -25 <= beta[79] <= 25
 -25 <= beta[80] <= 25
 -25 <= beta[81] <= 25
 -25 <= beta[82] <= 25
 -25 <= beta[83] <= 25
 -25 <= beta[84] <= 25
 -25 <= beta[85] <= 25
 -25 <= beta[86] <= 25
 -25 <= beta[87] <= 25
 -25 <= beta[88] <= 25
 -25 <= beta[89] <= 25
 -25 <= beta[90] <= 25
 -25 <= beta[91] <= 25
 -25 <= beta[92] <= 25
 -25 <= beta[93] <= 25
 -25 <= beta[94] <= 25
 -25 <= beta[95] <= 25
 -25 <= beta[96] <= 25
 -25 <= beta[97] <= 25
 -25 <= beta[98] <= 25
 -25 <= beta[99] <= 25
 -25 <= beta[100] <= 25
 -25 <= beta[101] <= 25
 -25 <= beta[102] <= 25
 -25 <= beta[103] <= 25
 -25 <= beta[104] <= 25
 -25 <= beta[105] <= 25
 -25 <= beta[106] <= 25
 -25 <= beta[107] <= 25
 -25 <= beta[108] <= 25
 -25 <= beta[109] <= 25
 -25 <= beta[110] <= 25
 -25 <= beta[111] <= 25
 -25 <= beta[112] <= 25
 -25 <= beta[113] <= 25
 -25 <= beta[114] <= 25
 -25 <= beta[115] <= 25
 -25 <= beta[116] <= 25
 -25 <= beta[117] <= 25
 -25 <= beta[118] <= 25
 -25 <= beta[119] <= 25
 -25 <= beta[120] <= 25
 -25 <= beta[121] <= 25
 -25 <= beta[122] <= 25
 -25 <= beta[123] <= 25
 -25 <= beta[124] <= 25
 -25 <= beta[125] <= 25
 -25 <= beta[126] <= 25
 -25 <= beta[127] <= 25
 -25 <= beta[128] <= 25
 -25 <= beta[129] <= 25
 -25 <= beta[130] <= 25
 -25 <= beta[131] <= 25
 -25 <= beta[132] <= 25
 -25 <= beta[133] <= 25
 -25 <= beta[134] <= 25
 -25 <= beta[135] <= 25
 -25 <= beta[136] <= 25
 -25 <= beta[137] <= 25
 -25 <= beta[138] <= 25
 -25 <= beta[139] <= 25
 -25 <= beta[140] <= 25
 -25 <= beta[141] <= 25
 -25 <= beta[142] <= 25
 -25 <= beta[143] <= 25
 -25 <= beta[144] <= 25
 -25 <= beta[145] <= 25
 -25 <= beta[146] <= 25
 -25 <= beta[147] <= 25
 -25 <= beta[148] <= 25
 -25 <= beta[149] <= 25
 -25 <= beta[150] <= 25
 -25 <= beta[151] <= 25
 -25 <= beta[152] <= 25
 -25 <= beta[153] <= 25
 -25 <= beta[154] <= 25
 -25 <= beta[155] <= 25
 -25 <= beta[156] <= 25
 -25 <= beta[157] <= 25
 -25 <= beta[158] <= 25
 -25 <= beta[159] <= 25
 -25 <= beta[160] <= 25
 -25 <= beta[161] <= 25
 -25 <= beta[162] <= 25
 -25 <= beta[163] <= 25
 -25 <= beta[164] <= 25
 -25 <= beta[165] <= 25
 -25 <= beta[166] <= 25
 -25 <= beta[167] <= 25
 -25 <= beta[168] <= 25
 -25 <= beta[169] <= 25
 -25 <= beta[170] <= 25
 -25 <= beta[171] <= 25
 -25 <= beta[172] <= 25
 -25 <= beta[173] <= 25
 -25 <= beta[174] <= 25
 -25 <= beta[175] <= 25
 -25 <= beta[176] <= 25
 -25 <= beta[177] <= 25
 -25 <= beta[178] <= 25
 -25 <= beta[179] <= 25
 -25 <= beta[180] <= 25
 -25 <= beta[181] <= 25
 -25 <= beta[182] <= 25
 -25 <= beta[183] <= 25
 -25 <= beta[184] <= 25
 -25 <= beta[185] <= 25
 -25 <= beta[186] <= 25
 -25 <= beta[187] <= 25
 -25 <= beta[188] <= 25
 -25 <= beta[189] <= 25
 -25 <= beta[190] <= 25
 -25 <= beta[191] <= 25
 -25 <= beta[192] <= 25
 -25 <= beta[193] <= 25
 -25 <= beta[194] <= 25
 -25 <= beta[195] <= 25
 -25 <= beta[196] <= 25
 -25 <= beta[197] <= 25
 -25 <= beta[198] <= 25
 -25 <= beta[199] <= 25
 -25 <= beta[200] <= 25
 -25 <= beta[201] <= 25
 -25 <= beta[202] <= 25
 -25 <= beta[203] <= 25
 -25 <= beta[204] <= 25
 -25 <= beta[205] <= 25
 -25 <= beta[206] <= 25
 -25 <= beta[207] <= 25
 -25 <= beta[208] <= 25
 -25 <= beta[209] <= 25
 -25 <= beta[210] <= 25
 -25 <= beta[211] <= 25
 -25 <= beta[212] <= 25
 -25 <= beta[213] <= 25
 -25 <= beta[214] <= 25
 -25 <= beta[215] <= 25
 -25 <= beta[216] <= 25
 -25 <= beta[217] <= 25
 -25 <= beta[218] <= 25
 -25 <= beta[219] <= 25
 -25 <= beta[220] <= 25
 -25 <= beta[221] <= 25
 -25 <= beta[222] <= 25
 -25 <= beta[223] <= 25
 -25 <= beta[224] <= 25
 -25 <= beta[225] <= 25
 -25 <= beta[226] <= 25
 -25 <= beta[227] <= 25
 -25 <= beta[228] <= 25
 -25 <= beta[229] <= 25
 -25 <= beta[230] <= 25
 -25 <= beta[231] <= 25
 -25 <= beta[232] <= 25
 -25 <= beta[233] <= 25
 -25 <= beta[234] <= 25
 -25 <= beta[235] <= 25
 -25 <= beta[236] <= 25
 -25 <= beta[237] <= 25
 -25 <= beta[238] <= 25
 -25 <= beta[239] <= 25
 -25 <= beta[240] <= 25
 -25 <= beta[241] <= 25
 -25 <= beta[242] <= 25
 -25 <= beta[243] <= 25
 -25 <= beta[244] <= 25
 -25 <= beta[245] <= 25
 -25 <= beta[246] <= 25
 -25 <= beta[247] <= 25
 -25 <= beta[248] <= 25
 -25 <= beta[249] <= 25
 -25 <= beta[250] <= 25
 -25 <= beta[251] <= 25
 -25 <= beta[252] <= 25
 -25 <= beta[253] <= 25
 -25 <= beta[254] <= 25
 -25 <= beta[255] <= 25
 -25 <= beta[256] <= 25
 -25 <= beta[257] <= 25
 -25 <= beta[258] <= 25
 -25 <= beta[259] <= 25
 -25 <= beta[260] <= 25
 -25 <= beta[261] <= 25
 -25 <= beta[262] <= 25
 -25 <= beta[263] <= 25
 -25 <= beta[264] <= 25
 -25 <= beta[265] <= 25
 -25 <= beta[266] <= 25
 -25 <= beta[267] <= 25
 -25 <= beta[268] <= 25
 -25 <= beta[269] <= 25
 -25 <= beta[270] <= 25
 -25 <= beta[271] <= 25
 -25 <= beta[272] <= 25
 -25 <= beta[273] <= 25
 -25 <= beta[274] <= 25
 -25 <= beta[275] <= 25
 -25 <= beta[276] <= 25
 -25 <= beta[277] <= 25
 -25 <= beta[278] <= 25
 -25 <= beta[279] <= 25
 -25 <= beta[280] <= 25
 -25 <= beta[281] <= 25
 -25 <= beta[282] <= 25
 -25 <= beta[283] <= 25
 -25 <= beta[284] <= 25
 -25 <= beta[285] <= 25
 -25 <= beta[286] <= 25
 -25 <= beta[287] <= 25
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
 selected[0] selected[1] selected[2] selected[3] selected[4] selected[5]
 selected[6] selected[7] selected[8] selected[9] selected[10] selected[11]
 selected[12] selected[13] selected[14] selected[15] selected[16]
 selected[17] selected[18] selected[19] selected[20] selected[21]
 selected[22] selected[23] selected[24] selected[25] selected[26]
 selected[27] selected[28] selected[29] selected[30] selected[31]
 selected[32] selected[33] selected[34] selected[35] selected[36]
 selected[37] selected[38] selected[39] selected[40] selected[41]
 selected[42] selected[43] selected[44] selected[45] selected[46]
 selected[47] selected[48] selected[49] selected[50] selected[51]
 selected[52] selected[53] selected[54] selected[55] selected[56]
 selected[57] selected[58] selected[59] selected[60] selected[61]
 selected[62] selected[63] selected[64] selected[65] selected[66]
 selected[67] selected[68] selected[69] selected[70] selected[71]
 selected[72] selected[73] selected[74] selected[75] selected[76]
 selected[77] selected[78] selected[79] selected[80] selected[81]
 selected[82] selected[83] selected[84] selected[85] selected[86]
 selected[87] selected[88] selected[89] selected[90] selected[91]
 selected[92] selected[93] selected[94] selected[95] selected[96]
 selected[97] selected[98] selected[99] selected[100] selected[101]
 selected[102] selected[103] selected[104] selected[105] selected[106]
 selected[107] selected[108] selected[109] selected[110] selected[111]
 selected[112] selected[113] selected[114] selected[115] selected[116]
 selected[117] selected[118] selected[119] selected[120] selected[121]
 selected[122] selected[123] selected[124] selected[125] selected[126]
 selected[127] selected[128] selected[129] selected[130] selected[131]
 selected[132] selected[133] selected[134] selected[135] selected[136]
 selected[137] selected[138] selected[139] selected[140] selected[141]
 selected[142] selected[143] selected[144] selected[145] selected[146]
 selected[147] selected[148] selected[149] selected[150] selected[151]
 selected[152] selected[153] selected[154] selected[155] selected[156]
 selected[157] selected[158] selected[159] selected[160] selected[161]
 selected[162] selected[163] selected[164] selected[165] selected[166]
 selected[167] selected[168] selected[169] selected[170] selected[171]
 selected[172] selected[173] selected[174] selected[175] selected[176]
 selected[177] selected[178] selected[179] selected[180] selected[181]
 selected[182] selected[183] selected[184] selected[185] selected[186]
 selected[187] selected[188] selected[189] selected[190] selected[191]
 selected[192] selected[193] selected[194] selected[195] selected[196]
 selected[197] selected[198] selected[199] selected[200] selected[201]
 selected[202] selected[203] selected[204] selected[205] selected[206]
 selected[207] selected[208] selected[209] selected[210] selected[211]
 selected[212] selected[213] selected[214] selected[215] selected[216]
 selected[217] selected[218] selected[219] selected[220] selected[221]
 selected[222] selected[223] selected[224] selected[225] selected[226]
 selected[227] selected[228] selected[229] selected[230] selected[231]
 selected[232] selected[233] selected[234] selected[235] selected[236]
 selected[237] selected[238] selected[239] selected[240] selected[241]
 selected[242] selected[243] selected[244] selected[245] selected[246]
 selected[247] selected[248] selected[249] selected[250] selected[251]
 selected[252] selected[253] selected[254] selected[255] selected[256]
 selected[257] selected[258] selected[259] selected[260] selected[261]
 selected[262] selected[263] selected[264] selected[265] selected[266]
 selected[267] selected[268] selected[269] selected[270] selected[271]
 selected[272] selected[273] selected[274] selected[275] selected[276]
 selected[277] selected[278] selected[279] selected[280] selected[281]
 selected[282] selected[283] selected[284] selected[285] selected[286]
 selected[287] selected[288] selected[289] selected[290] selected[291]
End
