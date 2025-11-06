benh_nhan = []
data_base = {}

def gui_thong_bao(benh_nhan, noi_dung_kham):
    pass

def luuthongtinxetnghiem(ma_so_benh_nhan, dia_diem_xet_nghiem, noi_dung_kham):
    data_base[len(data_base)+1] = {
        "ma_so_benh_nhan": ma_so_benh_nhan,
        "dia_diem_xet_nghiem": dia_diem_xet_nghiem,
        "noi_dung_kham": noi_dung_kham,
    }
    gui_thong_bao(ma_so_benh_nhan, noi_dung_kham)

INPUT = ["ma_so_benh_nhan", "dia_diem_xet_nghiem", "noi_dung_kham"]

while True:
    print("bam 1 de xac nhan")
    x = input(": ")
    if x == "1":
        dulieucanluu = []
        for stt,i in enumerate(INPUT):
            dulieucanluu.append(input(i))
        a = (luuthongtinxetnghiem(dulieucanluu[0],dulieucanluu[1],dulieucanluu[2]))
        gui_thong_bao(dulieucanluu[0], dulieucanluu[1])
        print("thao tac thanh cong")
            
        