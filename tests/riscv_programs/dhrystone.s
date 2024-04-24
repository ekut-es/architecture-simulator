
main:
addi	sp,sp,-128
sw	ra,124(sp)
sw	s0,120(sp)
sw	s1,116(sp)
sw	s2,112(sp)
sw	s3,108(sp)
sw	s4,104(sp)
sw	s5,100(sp)
sw	s6,96(sp)
sw	s7,92(sp)
sw	s8,88(sp)
lui	a5,0x4
addi	a5,a5,128 # 4080 <REC1>
lui	a4,0x7
sw	a5,-1796(a4) # 68fc <Next_Ptr_Glob>
addi	a3,a5,64
lui	a4,0x7
sw	a3,-1792(a4) # 6900 <Ptr_Glob>
sw	a5,64(a5)
sw	zero,68(a5)
addi	a4,zero,2
sw	a4,72(a5)
addi	a4,zero,40
sw	a4,76(a5)
lui	a4,0x4
addi	a4,a4,0 # 4000 <Proc_6+0x385c>
lw	t1,0(a4)
lw	a7,4(a4)
lw	a6,8(a4)
lw	a0,12(a4)
lw	a1,16(a4)
lw	a2,20(a4)
lw	a3,24(a4)
sw	t1,80(a5)
sw	a7,84(a5)
sw	a6,88(a5)
sw	a0,92(a5)
sw	a1,96(a5)
sw	a2,100(a5)
sw	a3,104(a5)
lhu	a3,28(a4)
sh	a3,108(a5)
lbu	a4,30(a4)
sb	a4,110(a5)
lui	a5,0x4
addi	a5,a5,32 # 4020 <Proc_6+0x387c>
lw	a7,0(a5)
lw	a6,4(a5)
lw	a0,8(a5)
lw	a1,12(a5)
lw	a2,16(a5)
lw	a3,20(a5)
lw	a4,24(a5)
sw	a7,36(sp)
sw	a6,40(sp)
sw	a0,44(sp)
sw	a1,48(sp)
sw	a2,52(sp)
sw	a3,56(sp)
sw	a4,60(sp)
lhu	a4,28(a5)
sh	a4,64(sp)
lbu	a5,30(a5)
sb	a5,66(sp)
lui	a5,0x5
addi	a4,zero,10
sw	a4,-2012(a5) # 4824 <Arr_2_Glob+0x65c>
addi	s4,zero,1
lui	s2,0x4
addi	s2,s2,64 # 4040 <Proc_6+0x389c>
lui	s8,0x7
lui	s7,0x4
addi	s7,s7,256 # 4100 <Arr_1_Glob>
lui	s1,0x4
addi	s1,s1,96 # 4060 <Proc_6+0x38bc>
lui	s6,0x7
jal	zero, main+0x1e4
addi	s0,s0,1
andi	s0,s0,255
lbu	a5,-1808(s3)
bltu	a5,s0, main+0x1bc
addi	a1,zero,67
addi	a0,s0,0
jal	ra, Func_1
lw	a5,68(sp)
bne	a0,a5, main+0x134
addi	a1,sp,68
addi	a0,zero,0
jal	ra, Proc_6
lw	a6,0(s1)
lw	a0,4(s1)
lw	a1,8(s1)
lw	a2,12(s1)
lw	a3,16(s1)
lw	a4,20(s1)
lw	a5,24(s1)
sw	a6,4(sp)
sw	a0,8(sp)
sw	a1,12(sp)
sw	a2,16(sp)
sw	a3,20(sp)
sw	a4,24(sp)
sw	a5,28(sp)
lhu	a5,28(s1)
sh	a5,32(sp)
lbu	a5,30(s1)
sb	a5,34(sp)
sw	s4,-1800(s6) # 68f8 <Int_Glob>
addi	s5,s4,0
jal	zero, main+0x134
addi	s5,zero,3
slli	a5,s5,0x1
add	a5,a5,s5
lw	a4,72(sp)
div	a5,a5,a4
sw	a5,76(sp)
addi	a0,sp,76
jal	ra, Proc_2
addi	s4,s4,1
addi	a5,zero,51
beq	s4,a5, main+0x2b4
jal	ra, Proc_5
jal	ra, Proc_4
lw	a6,0(s2)
lw	a0,4(s2)
lw	a1,8(s2)
lw	a2,12(s2)
lw	a3,16(s2)
lw	a4,20(s2)
lw	a5,24(s2)
sw	a6,4(sp)
sw	a0,8(sp)
sw	a1,12(sp)
sw	a2,16(sp)
sw	a3,20(sp)
sw	a4,24(sp)
sw	a5,28(sp)
lhu	a5,28(s2)
sh	a5,32(sp)
lbu	a5,30(s2)
sb	a5,34(sp)
addi	a5,zero,1
sw	a5,68(sp)
addi	a1,sp,4
addi	a0,sp,36
jal	ra, Func_2
sltiu	a0,a0,1
sw	a0,-1804(s8) # 68f4 <Bool_Glob>
addi	a5,zero,7
sw	a5,72(sp)
addi	a2,sp,72
addi	a1,zero,3
addi	a0,zero,2
jal	ra, Proc_7
addi	a5,zero,3
sw	a5,76(sp)
lw	a3,72(sp)
addi	a2,zero,3
lui	a1,0x4
addi	a1,a1,456 # 41c8 <Arr_2_Glob>
addi	a0,s7,0
jal	ra, Proc_8
lui	a5,0x7
lw	a0,-1792(a5) # 6900 <Ptr_Glob>
jal	ra, Proc_1
lui	a5,0x7
lbu	a4,-1808(a5) # 68f0 <Ch_2_Glob>
addi	a5,zero,64
bgeu	a5,a4, main+0x1b8
addi	s0,zero,65
addi	s5,zero,3
lui	s3,0x7
jal	zero, main+0x144
addi	a7,zero,10
ecall
lw	ra,124(sp)
lw	s0,120(sp)
lw	s1,116(sp)
lw	s2,112(sp)
lw	s3,108(sp)
lw	s4,104(sp)
lw	s5,100(sp)
lw	s6,96(sp)
lw	s7,92(sp)
lw	s8,88(sp)
addi	sp,sp,128
jalr	zero,0(ra)

strcmp:
or	a4,a0,a1
addi	t2,zero,-1
andi	a4,a4,3
bne	a4,zero, strcmp+0x10c
lui	a5,0x7f7f8
addi	a5,a5,-129 # 7f7f7f7f <Ptr_Glob+0x7f7f167f>
lw	a2,0(a0)
lw	a3,0(a1)
and	t0,a2,a5
or	t1,a2,a5
add	t0,t0,a5
or	t0,t0,t1
bne	t0,t2, strcmp+0x134
bne	a2,a3, strcmp+0xc0
lw	a2,4(a0)
lw	a3,4(a1)
and	t0,a2,a5
or	t1,a2,a5
add	t0,t0,a5
or	t0,t0,t1
bne	t0,t2, strcmp+0x12c
bne	a2,a3, strcmp+0xc0
lw	a2,8(a0)
lw	a3,8(a1)
and	t0,a2,a5
or	t1,a2,a5
add	t0,t0,a5
or	t0,t0,t1
bne	t0,t2, strcmp+0x140
bne	a2,a3, strcmp+0xc0
lw	a2,12(a0)
lw	a3,12(a1)
and	t0,a2,a5
or	t1,a2,a5
add	t0,t0,a5
or	t0,t0,t1
bne	t0,t2, strcmp+0x154
bne	a2,a3, strcmp+0xc0
lw	a2,16(a0)
lw	a3,16(a1)
and	t0,a2,a5
or	t1,a2,a5
add	t0,t0,a5
or	t0,t0,t1
bne	t0,t2, strcmp+0x168
addi	a0,a0,20
addi	a1,a1,20
beq	a2,a3, strcmp+0x18
slli	a4,a2,0x10
slli	a5,a3,0x10
bne	a4,a5, strcmp+0xe4
srli	a4,a2,0x10
srli	a5,a3,0x10
sub	a0,a4,a5
andi	a1,a0,255
bne	a1,zero, strcmp+0xfc
jalr	zero,0(ra)
srli	a4,a4,0x10
srli	a5,a5,0x10
sub	a0,a4,a5
andi	a1,a0,255
bne	a1,zero, strcmp+0xfc
jalr	zero,0(ra)
andi	a4,a4,255
andi	a5,a5,255
sub	a0,a4,a5
jalr	zero,0(ra)
lbu	a2,0(a0)
lbu	a3,0(a1)
addi	a0,a0,1
addi	a1,a1,1
bne	a2,a3, strcmp+0x124
bne	a2,zero, strcmp+0x10c
sub	a0,a2,a3
jalr	zero,0(ra)
addi	a0,a0,4
addi	a1,a1,4
bne	a2,a3, strcmp+0x10c
addi	a0,zero,0
jalr	zero,0(ra)
addi	a0,a0,8
addi	a1,a1,8
bne	a2,a3, strcmp+0x10c
addi	a0,zero,0
jalr	zero,0(ra)
addi	a0,a0,12
addi	a1,a1,12
bne	a2,a3, strcmp+0x10c
addi	a0,zero,0
jalr	zero,0(ra)
addi	a0,a0,16
addi	a1,a1,16
bne	a2,a3, strcmp+0x10c
addi	a0,zero,0
jalr	zero,0(ra)

Proc_2:
lui	a5,0x7
lbu	a4,-1807(a5) # 68f1 <Ch_1_Glob>
addi	a5,zero,65
beq	a4,a5, Proc_2+0x14
jalr	zero,0(ra)
lw	a5,0(a0)
addi	a5,a5,9
lui	a4,0x7
lw	a4,-1800(a4) # 68f8 <Int_Glob>
sub	a5,a5,a4
sw	a5,0(a0)
jal	zero, Proc_2+0x10

Proc_3:
addi	sp,sp,-16
sw	ra,12(sp)
lui	a5,0x7
lw	a5,-1792(a5) # 6900 <Ptr_Glob>
beq	a5,zero, Proc_3+0x1c
lw	a5,0(a5)
sw	a5,0(a0)
lui	a5,0x7
lw	a2,-1792(a5) # 6900 <Ptr_Glob>
addi	a2,a2,12
lui	a5,0x7
lw	a1,-1800(a5) # 68f8 <Int_Glob>
addi	a0,zero,10
jal	ra, Proc_7
lw	ra,12(sp)
addi	sp,sp,16
jalr	zero,0(ra)

Proc_1:
addi	sp,sp,-16
sw	ra,12(sp)
sw	s0,8(sp)
sw	s1,4(sp)
addi	s1,a0,0
lw	s0,0(a0)
lui	a5,0x7
lw	a5,-1792(a5) # 6900 <Ptr_Glob>
lw	t4,0(a5)
lw	t3,4(a5)
lw	t1,8(a5)
lw	a7,16(a5)
lw	a6,20(a5)
lw	a0,24(a5)
lw	a1,28(a5)
lw	a2,32(a5)
lw	a3,36(a5)
lw	a4,40(a5)
lw	a5,44(a5)
sw	t4,0(s0)
sw	t3,4(s0)
sw	t1,8(s0)
sw	a7,16(s0)
sw	a6,20(s0)
sw	a0,24(s0)
sw	a1,28(s0)
sw	a2,32(s0)
sw	a3,36(s0)
sw	a4,40(s0)
sw	a5,44(s0)
addi	a5,zero,5
sw	a5,12(s1)
sw	a5,12(s0)
lw	a5,0(s1)
sw	a5,0(s0)
addi	a0,s0,0
jal	ra, Proc_3
lw	a5,4(s0)
beq	a5,zero, Proc_1+0x114
lw	a5,0(s1)
lw	t5,0(a5)
lw	t4,4(a5)
lw	t3,8(a5)
lw	t1,12(a5)
lw	a7,16(a5)
lw	a6,20(a5)
lw	a0,24(a5)
lw	a1,28(a5)
lw	a2,32(a5)
lw	a3,36(a5)
lw	a4,40(a5)
lw	a5,44(a5)
sw	t5,0(s1)
sw	t4,4(s1)
sw	t3,8(s1)
sw	t1,12(s1)
sw	a7,16(s1)
sw	a6,20(s1)
sw	a0,24(s1)
sw	a1,28(s1)
sw	a2,32(s1)
sw	a3,36(s1)
sw	a4,40(s1)
sw	a5,44(s1)
lw	ra,12(sp)
lw	s0,8(sp)
lw	s1,4(sp)
addi	sp,sp,16
jalr	zero,0(ra)
addi	a5,zero,6
sw	a5,12(s0)
addi	a1,s0,8
lw	a0,8(s1)
jal	ra, Proc_6
lui	a5,0x7
lw	a5,-1792(a5) # 6900 <Ptr_Glob>
lw	a5,0(a5)
sw	a5,0(s0)
addi	a2,s0,12
addi	a1,zero,10
lw	a0,12(s0)
jal	ra, Proc_7
jal	zero, Proc_1+0x100

Proc_4:
lui	a4,0x7
lui	a5,0x7
lbu	a5,-1807(a5) # 68f1 <Ch_1_Glob>
addi	a5,a5,-65
sltiu	a5,a5,1
lw	a3,-1804(a4) # 68f4 <Bool_Glob>
or	a5,a5,a3
sw	a5,-1804(a4)
lui	a5,0x7
addi	a4,zero,66
sb	a4,-1808(a5) # 68f0 <Ch_2_Glob>
jalr	zero,0(ra)

Proc_5:
lui	a5,0x7
addi	a4,zero,65
sb	a4,-1807(a5) # 68f1 <Ch_1_Glob>
lui	a5,0x7
sw	zero,-1804(a5) # 68f4 <Bool_Glob>
jalr	zero,0(ra)

Proc_7:
addi	a0,a0,2
add	a0,a0,a1
sw	a0,0(a2)
jalr	zero,0(ra)

Proc_8:
addi	a4,a2,5
slli	a6,a4,0x2
add	a0,a0,a6
sw	a3,0(a0)
sw	a3,4(a0)
sw	a4,120(a0)
addi	a3,zero,200
mul	a3,a4,a3
slli	a5,a2,0x2
add	a5,a5,a3
add	a5,a1,a5
sw	a4,20(a5)
sw	a4,24(a5)
lw	a4,16(a5)
addi	a4,a4,1
sw	a4,16(a5)
lw	a4,0(a0)
add	a1,a1,a3
lui	a5,0x1
add	a5,a5,a1
add	a5,a5,a6
sw	a4,-96(a5) # fa0 <Proc_6+0x7fc>
lui	a5,0x7
addi	a4,zero,5
sw	a4,-1800(a5) # 68f8 <Int_Glob>
jalr	zero,0(ra)

Func_1:
andi	a0,a0,255
andi	a1,a1,255
beq	a0,a1, Func_1+0x14
addi	a0,zero,0
jalr	zero,0(ra)
lui	a5,0x7
sb	a0,-1807(a5) # 68f1 <Ch_1_Glob>
addi	a0,zero,1
jalr	zero,0(ra)

Func_2:
addi	sp,sp,-32
sw	ra,28(sp)
sw	s0,24(sp)
sw	s1,20(sp)
sw	s2,16(sp)
sw	s3,12(sp)
addi	s1,a0,0
addi	s2,a1,0
addi	s0,zero,2
addi	s3,zero,2
add	a4,s2,s0
add	a5,s1,s0
lbu	a1,1(a4)
lbu	a0,0(a5)
jal	ra, Func_1
sltiu	a0,a0,1
add	s0,s0,a0
bge	s3,s0, Func_2+0x28
addi	a1,s2,0
addi	a0,s1,0
jal	ra, strcmp
addi	a5,zero,0
bge	zero,a0, Func_2+0x6c
addi	s0,s0,7
lui	a5,0x7
sw	s0,-1800(a5) # 68f8 <Int_Glob>
addi	a5,zero,1
addi	a0,a5,0
lw	ra,28(sp)
lw	s0,24(sp)
lw	s1,20(sp)
lw	s2,16(sp)
lw	s3,12(sp)
addi	sp,sp,32
jalr	zero,0(ra)

Func_3:
addi	a0,a0,-2
sltiu	a0,a0,1
jalr	zero,0(ra)

Proc_6:
addi	sp,sp,-16
sw	ra,12(sp)
sw	s0,8(sp)
sw	s1,4(sp)
addi	s0,a0,0
addi	s1,a1,0
jal	ra, Func_3
addi	a5,s0,0
bne	a0,zero, Proc_6+0x28
addi	a5,zero,3
sw	a5,0(s1)
addi	a5,zero,2
beq	s0,a5, Proc_6+0x8c
bltu	a5,s0, Proc_6+0x54
beq	s0,zero, Proc_6+0x68
lui	a5,0x7
lw	a4,-1800(a5) # 68f8 <Int_Glob>
addi	a5,zero,100
bge	a5,a4, Proc_6+0x80
sw	zero,0(s1)
jal	zero, Proc_6+0x6c
addi	a5,zero,4
bne	s0,a5, Proc_6+0x6c
addi	a5,zero,2
sw	a5,0(s1)
jal	zero, Proc_6+0x6c
sw	zero,0(s1)
lw	ra,12(sp)
lw	s0,8(sp)
lw	s1,4(sp)
addi	sp,sp,16
jalr	zero,0(ra)
addi	a5,zero,3
sw	a5,0(s1)
jal	zero, Proc_6+0x6c
addi	a5,zero,1
sw	a5,0(s1)
jal	zero, Proc_6+0x6c


.data
rodata: .word 0x44485259, 0x53544f4e, 0x45205052, 0x4f475241, 0x4d2c2053, 0x4f4d4520, 0x53545249, 0x4e470000, 0x44485259, 0x53544f4e, 0x45205052, 0x4f475241, 0x4d2c2031, 0x27535420, 0x53545249, 0x4e470000, 0x44485259, 0x53544f4e, 0x45205052, 0x4f475241, 0x4d2c2032, 0x274e4420, 0x53545249, 0x4e470000, 0x44485259, 0x53544f4e, 0x45205052, 0x4f475241, 0x4d2c2033, 0x27524420, 0x53545249, 0x4e4700
