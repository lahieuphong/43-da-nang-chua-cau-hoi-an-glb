# v47 roof curve

- Base là v46 (mặt trước v44, xoá viền nâu đầu sau).
- Áp đường cong parabol lên-ngang-xuống cho mái ngói (mat [16, 17, 18, 19, 20, 21, 22, 23]).
- Y_offset(X) = -0.25 * (|X|/5.5)²
  - Giữa (X=0): offset=0 (không đổi)
  - Hai đầu (|X|=5.5): offset=-0.25m
- Không xoá tam giác nào, giữ nguyên index arrays.
- Cùng profile đường cong với thanh gỗ nâu (mat13).
