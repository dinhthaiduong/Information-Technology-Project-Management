PROMPT: dict[str, str | list[str]] = {}

SPECIAL_CHARS = ["\\", '"']
# MATCH (n) DETACH DELETE n;

PROMPT["SYSTEM_INTRUCT"] = """
Thực hiện các bước sau:

0. Không viết bất kỳ đoạn mã nào.
1. Xác định tất cả các thực thể và phân loại chúng thành ngành đào tạo, giảng viên, môn học, ... Chi tiết hóa mô tả và từ khóa quan trọng của từng thực thể.
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì, từ thuộc về, hiểu, sử dụng, liên quan tới...
3. Trả kết quả dưới dạng ("entity", "loại", "Tên", "mô tả") cho loại thực thể hoặc ("relationship", "Nút 1", "Nút 2", "mô tả", "từ khóa") cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu với "entity" hoặc "relationship".

Ví dụ:

Với đầu 1 vào:
các giảng viên học phần: kiến trúc máy tính - computer architecture
Tên giảng viên: Nguyễn Đình Việt, chức danh: PGS. TS, chuyên ngành: Đảm bảo toán học cho máy tính và hệ thống tính toán, đơn vị: Trường ĐHCN
Tên giảng viên: Nguyễn Ngọc Hoá, chức danh: TS, chuyên ngành: Công nghệ thông tin, đơn vị: Trường ĐHCN

Kết quả đầu ra 1 sẽ là:
[
("entity", “học phần”, “Kiến trúc máy tính”, “Nghiên cứu về cấu trúc và hoạt động của máy tính, từ các thành phần phần cứng cơ bản đến cách chúng tương tác với phần mềm”),
("entity", “tên tiếng Anh”, “Computer Architecture”, “Là tên tiếng Anh của học phần Kiến trúc máy tính”),
("entity", “giảng viên”, "Nguyễn Đình Việt", “Nguyễn Đình Việt là 1 Phó giáo sư, Tiến sĩ chuyên ngành Đảm bảo toán học cho máy tính và hệ thống tính toán của trường Đại học Công Nghệ”),
("entity", “giảng viên”, “Nguyễn Ngọc Hoá”, "Nguyễn Ngọc Hoá là 1 Tiến sĩ chuyên ngành Công nghệ thông tin của trường Đại học Công Nghệ"),
("entity", “chức danh”, “PGS. TS”, “Viết tắt cho Phó giáo sư, Tiến sĩ”),
("entity", “chức danh”, “TS”, “Viết tắt cho Tiến sĩ”),
("entity", “chuyên ngành”, “Đảm bảo toán học cho máy tính và hệ thống tính toán”, “Ứng dụng toán học trong Công nghệ thông tin và Khoa học máy tính”),
("entity", “chuyên ngành”, “Công nghệ thông tin”, “Nghiên cứu, phát triển và ứng dụng các hệ thống, công cụ, và phương pháp nhằm xử lý, lưu trữ, truyền tải và bảo vệ thông tin”),
("entity", “đơn vị”, “Trường ĐHCN”, “Là trường Đại Học Công Nghệ - Đại học Quốc gia Hà Nội, có tên viết tắt là UET”),
("relationship", “Kiến trúc máy tính”, “Computer Architecture”, “Computer Architecture là tên tiếng Anh của học phần Kiến trúc máy tính, phần lớn các chương trình đào tạo Chất lượng cao ở Đại Học Công Nghệ đều sử dụng tiếng Anh”, “giảng dạy, học phần, môn học, tiếng Anh”),
("relationship", "Nguyễn Đình Việt", “kiến trúc máy tính”, "Nguyễn Đình Việt là giảng viên dạy học phần Kiến trúc máy tính”, “giảng viên, giảng dạy, học phần, môn học”),
("relationship", “Nguyễn Ngọc Hoá”, “kiến trúc máy tính”, "Nguyễn Ngọc Hoá là giảng viên dạy học phần Kiến trúc máy tính”, “giảng viên, giảng dạy, học phần, môn học”),
("relationship", "Nguyễn Đình Việt", "Nguyễn Ngọc Hoá", "Nguyễn Đình Việt và Nguyễn Ngọc Hoá đều là giảng viên dạy môn Kiến trúc máy tính của trường Đại Học Công Nghệ - Đại học Quốc gia Hà Nội” , “giảng viên, Kiến trúc máy tính, môn học, học phần, giảng dạy, đại học”),
("relationship", "Nguyễn Đình Việt", "PGS. TS", “Nguyễn Đình Việt có học hàm, học vị là Phó giáo sư, Tiến sĩ”, “học hàm, học vị, chức danh, danh hiệu”),
("relationship", "Nguyễn Ngọc Hoá”, "TS", “Nguyễn Ngọc Hoá có học hàm, học vị là Tiến sĩ”, “học hàm, học vị, chức danh, danh hiệu”),
("relationship", "Nguyễn Đình Việt", "Đảm bảo toán học cho máy tính và hệ thống tính toán", “Chuyên ngành của Nguyễn Đình Việt là Đảm bảo toán học cho máy tính và hệ thống tính toán”, “giảng viên, chuyên ngành, năng lực”),
("relationship", "Nguyễn Ngọc Hoá”, "Công nghệ thông tin", “Chuyên ngành của Nguyễn Ngọc Hoá là Công nghệ thông tin”, “chuyên ngành, năng lực”),
("relationship", "Nguyễn Đình Việt”, "Trường ĐHCN", “Nguyễn Đình Việt là giảng viên của trường Đại Học Công Nghệ - Đại học Quốc gia Hà Nội”, “giảng viên, giảng dạy, đơn vị, trường, đại học,”),
("relationship", "Nguyễn Ngọc Hoá”, "Trường ĐHCN", “Nguyễn Ngọc Hoá là giảng viên của trường Đại Học Công Nghệ - Đại học Quốc gia Hà Nội”, “giảng viên, giảng dạy, đơn vị, trường, đại học,”),
]

Với đầu vào 2:
Thông tin chung về học phần: toán học rời rạc 
Tên học phần:
Tiếng Việt: Toán học rời rạc 
Tiếng Anh: Discrete Mathematics
Mã số học phần: INT 1050 
Số tín chỉ: 4 Giờ tín chỉ đối với các hoạt động (LTThHTH): 6000 
Học phần tiên quyết (tên và mã số học phần): Không yêu cầu HPTQ 
Các yêu cầu đối với học phần (nếu có): Không có 
Bộ môn Khoa phụ trách học phần: Bộ môn KH&KT TT Khoa CNTT
Mục tiêu học phần: toán học rời rạc
Kiến thức: Cơ sở toán học cho ngành công nghệ thông tin
Kỹ năng: áp dụng phương pháp tư duy và suy luận toán học để giải quyết các vấn đề trong lĩnh vực khoa học và công nghệ.
Chuẩn đầu ra: toán học rời rạc
Chuẩn đầu ra học phần: Mã Nội dung chuẩn đầu ra
CĐR (Bắt đầu bằng động từ theo thang Bloom) Kiến thức
CLO1 Hiểu được các khái niệm cơ bản về tư duy logic các phương pháp toán trên tập các đối tượng rời rạc các lược đồ xây dựng thuật toán
CLO2 Hiểu và vận dụng được các kiến thức cơ bản của lý thuyết đồ thị
CLO3 Hiểu nguyên tắc hoạt động các mô hình tính toán trong các máy tính toán hiện đại
Kỹ năng
CLO4 Hiểu và vận dụng được tư duy giải quyết vấn đề dựa trên tư duy quy nạp toán học và đệ quy 
Nội dung chi tiết học phần: toán học rời rạc
Chương 1. Lô gích và chứng minh (10 tiết)
1.1. Logic mệnh đề
1.2. Logic lượng từ
1.3. Các lượng từ lồng nhau
1.4. Các quy tắc suy diễn
1.5. Các phương pháp chứng minh
1.6. Đại số Boolean
Chương 2. Thuật toán lý thuyết số và ứng dụng (8 tiết)
2.1. Thuật toán
2.2. Biểu diễn số nguyên
2.3. Thuật toán Euclid
2.4. Thuật toán mã hoá RSA
Hình thức tổ chức dạy học: toán học rời rạc
Lịch trình dạy cụ thể: TOÁN HỌC RỜI RẠC 
Tuần Nội dung giảng dạy lý thuyết thực hành Nội dung sinh viên tự học 
1 Logic mệnh đề: Lý thuyết Bài tập Bài tập bổ sung Logic vị từ. Lượng từ: Lý thuyết Bài tập Bài tập bổ sung 
2 Các lượng từ lồng nhau: Lý thuyết Bài tập Bài tập bổ sung Các quy tắc suy diễn: Lý thuyết Bài tập Bài tập bổ sung
3 Các phương pháp chứng minh: Lý thuyết Bài tập Bài tập bổ sung Thuật toán: Lý thuyết Bài tập Bài tập bổ sung 

Kết quả đầu ra 2 sẽ là:
[
("entity", “học phần”, “Toán học rời rạc”, “Nghiên cứu các khái niệm như số học, lý thuyết đồ thị, lý thuyết tập hợp, lý thuyết xác suất rời rạc, đếm, lý thuyết tự động, và các cấu trúc toán học có tính chất rời rạc”),
("entity", “tên tiếng Anh”, “Discrete Mathematics”, “Là tên tiếng Anh của học phần Toán học rời rạc”),
("entity", “mã số học phần”, “INT 1050”, “Là mã số học phần của học phần Toán học rời rạc”),
("entity", “số tín chỉ”, “4”, “Là số tín chỉ của học phần Toán học rời rạc”),
("entity", “học phần tiên quyết”, “Không yêu cầu”, “Là yêu cầu học phần tiên quyết để học Toán học rời rạc”),
("entity", “yêu cầu đối với học phần”, “Không có”, “Là yêu cầu để học Toán học rời rạc”),
("entity", “bộ môn Khoa phụ trách”, “Bộ môn KH&KT TT Khoa CNTT”, “Bộ Khoa phụ trách việc giảng dạy học phần Toán học rời rạc”),
("entity", “mục tiêu kiến thức”, “Cơ sở toán học cho ngành công nghệ thông tin”, “Mục tiêu cần đạt của học phần Toán học rời rạc”),
("entity", “mục tiêu kỹ năng”, “Áp dụng phương pháp tư duy và suy luận toán học để giải quyết các vấn đề trong lĩnh vực khoa học và công nghệ”, “Mục tiêu cần đạt của học phần Toán học rời rạc”),
("entity", “chuẩn đầu ra kiến thức", “CLO1”, “Chuẩn đầu ra kiến thức cấp 1”),
("entity", “chuẩn đầu ra kiến thức", “CLO1”, “Chuẩn đầu ra kiến thức cấp 2”),
("entity", “chuẩn đầu ra kiến thức”, “CLO2”, “Chuẩn đầu ra kiến thức cấp 3”),
("entity", “chuẩn đầu ra kỹ năng", “CLO4”, “Chuẩn đầu ra kỹ năng cấp 1”),
("entity", “nội dung học phần”, “Chương 1. Lô gích và chứng minh”, “Nội dung chi tiết của học phần Toán rời rạc”),
("entity", “nội dung học phần”, “Chương 2. Thuật toán lý thuyết số và ứng dụng”, “Nội dung chi tiết của học phần Toán rời rạc”),
("entity", “số tiết”, “10 tiết”, “Số tiết cho 1 chương”),
("entity", “số tiết”, “8 tiết”, “Số tiết cho 1 chương”),
("entity", “lịch trình giảng dạy”, “Tuần 1”, “Lịch trình giảng dạy chi tiết của học phần Toán rời rạc”),
("entity", “lịch trình giảng dạy”, “Tuần 2”, “Lịch trình giảng dạy chi tiết của học phần Toán rời rạc”),
("entity", “lịch trình giảng dạy”, “Tuần 3”, “Lịch trình giảng dạy chi tiết của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Logic mệnh đề”, “Nội dung giảng dạy tuần 1 của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Logic vị từ”, “Nội dung giảng dạy tuần 1 của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Các lượng từ lồng nhau”, “Nội dung giảng dạy tuần 2 của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Các quy tắc suy diễn”, “Nội dung giảng dạy tuần 2 của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Các phương pháp chứng minh”, “Nội dung giảng dạy tuần 3 của học phần Toán rời rạc”),
("entity", “nội dung giảng dạy”, “Thuật toán”, “Nội dung giảng dạy tuần 3 của học phần Toán rời rạc”),
("relationship", “Toán học rời rạc”, "Discrete Mathematics”, “Discrete Mathematics là tên tiếng Anh của học phần Toán học rời rạc, phần lớn các chương trình đào tạo Chất lượng cao ở Đại Học Công Nghệ đều sử dụng tiếng Anh”, “giảng dạy, học phần, môn học, tiếng Anh”),
("relationship", "Toán học rời rạc", “INT 1050”, “INT 1050 là mã số học phần của học phần Toán học rời rạc”, “mã môn học, mã, học phần”),
("relationship", "Toán học rời rạc", “4”, “4 là mã số tín chỉ của học phần Toán học rời rạc”, “tín chỉ, học phần”),
("relationship", "Toán học rời rạc", “Không yêu cầu”, “Học phần Toán học rời rạc không yêu cầu cần có học phần tiên quyết”, “học phần tiên quyết, học phần”),
("relationship", "Toán học rời rạc", “Không có”, “Học phần Toán học rời rạc không có yêu cầu đối với học phần”, “yêu cầu học phần, học phần”),
("relationship", "Toán học rời rạc", “Bộ môn KH&KT TT Khoa CNTT”, “Bộ môn KH&KT TT Khoa CNTT là Khoa phụ trách cho học phần Toán rời rạc”, “khoa, phụ trách, giảng dạy, học phần”),
("relationship", "Toán học rời rạc", “Cơ sở toán học cho ngành công nghệ thông tin”, “Mục tiêu kiến thức của học phần Toán học rời rạc là hiểu được cơ sở toán học cho ngành công nghệ thông tin”, “mục tiêu, kiến thức, học phần”),
("relationship", "Toán học rời rạc", “Áp dụng phương pháp tư duy và suy luận toán học để giải quyết các vấn đề trong lĩnh vực khoa học và công nghệ”, “Mục tiêu kỹ năng của học phần Toán học rời rạc là áp dụng phương pháp tư duy và suy luận toán học để giải quyết các vấn đề trong lĩnh vực khoa học và công nghệ”, “mục tiêu, kỹ năng, học phần”),
("relationship", "Toán học rời rạc", “CLO1”, “CLO1 là hiểu được các khái niệm cơ bản về tư duy logic các phương pháp toán trên tập các đối tượng rời rạc các lược đồ xây dựng thuật toán", “đầu ra, kiến thức, học phần”),
("relationship", "Toán học rời rạc", “CLO2”, “CLO2 là hiểu và vận dụng được các kiến thức cơ bản của lý thuyết đồ thị”, “đầu ra, kiến thức, học phần”),
("relationship", "Toán học rời rạc", “CLO3”, “CLO3 là hiểu nguyên tắc hoạt động các mô hình tính toán trong các máy tính toán hiện đại", “đầu ra, kiến thức, học phần”),
("relationship", "Toán học rời rạc", “CLO4”, “CLO4 là hiểu và vận dụng được tư duy giải quyết vấn đề dựa trên tư duy quy nạp toán học và đệ quy ”, “đầu ra, kỹ năng, học phần”),
("relationship", "Toán học rời rạc", “Chương 1. Lô gích và chứng minh”, “Chương 1. Thuật toán lý thuyết số và ứng dụng là chương đầu tiên của học phần Toán học rời rạc”, “chương trình, giảng dạy, học phần”),
("relationship", "Toán học rời rạc", “Chương 2. Thuật toán lý thuyết số và ứng dụng”, “Chương 2. Thuật toán lý thuyết số và ứng dụng là chương thứ hai của học phần Toán học rời rạc”, “chương trình, giảng dạy, học phần”),
("relationship", “Chương 1. Lô gích và chứng minh”, “10 tiết”,  “Chương 1. Thuật toán lý thuyết số và ứng dụng sẽ được giảng dạy trong 10 tiết”, “chương trình, lịch trình, giảng dạy, học phần, thời gian”),
("relationship", “Chương 2. Thuật toán lý thuyết số và ứng dụng”, “8 tiết”,  “Chương 2. Thuật toán lý thuyết số và ứng dụng sẽ được giảng dạy trong 8 tiết”, “chương trình, lịch trình, giảng dạy, học phần, thời gian”),
("relationship", "Toán học rời rạc", “Tuần 1”, “Tuần 1 trong lịch trình giảng dạy của học phần Toán học rời rạc”, “lịch trình, giảng dạy, học phần”),
("relationship", "Toán học rời rạc", “Tuần 2”, “Tuần 2 trong lịch trình giảng dạy của học phần Toán học rời rạc”, “lịch trình, giảng dạy, học phần”),
("relationship", "Toán học rời rạc", “Tuần 3”, “Tuần 3 trong lịch trình giảng dạy của học phần Toán học rời rạc”, “lịch trình, giảng dạy, học phần”),
("relationship", “Tuần 1”, "Logic mệnh đề", “Tuần 1 sẽ học về Logic mệnh đề”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
("relationship", “Tuần 1”, “Logic vị từ", “Tuần 1 sẽ học về Logic vị từ”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
("relationship", “Tuần 2”, "Các lượng từ lồng nhau", “Tuần 2 sẽ học về Các lượng từ lồng nhau”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
("relationship", “Tuần 2”, "Các quy tắc suy diễn", “Tuần 2 sẽ học về Các quy tắc suy diễn”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
("relationship", “Tuần 3”, "Các phương pháp chứng minh", “Tuần 3 sẽ học về Các phương pháp chứng minh”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
("relationship", “Tuần 3”, "Các phương pháp chứng minh", “Tuần 3 sẽ học về Các phương pháp chứng minh”, “lịch trình, nội dung, giảng dạy, bài giảng, học phần”),
]

Với đầu 3 vào:
Danh mục tài liệu tham khảo học phần Đại số - Algebra là:
Tài liệu bắt buộc
1. Nguyễn Đình Trí, Lê Trọng Vinh, Dương Thuỷ Vĩ. Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007.
2. Nguyễn Hữu Việt Hưng. Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004.
Tài liệu tham khảo thêm
1. Ron Lardson, Edward, Falvo. Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009.
2. Anton Rorres. Elementary Linear Algebra, 11th- edition. Wiley, 2013.

Kết quả đầu ra 3 sẽ là:
[
("entity", “học phần”, “Đại số”, “Nghiên cứu về các cấu trúc đại số và các phép toán, tập trung vào lý thuyết và ứng dụng của các đối tượng đại số, bao gồm các nhóm, vành, trường, ma trận, không gian vector và nhiều khái niệm khác”),
("entity", “tài liệu tham khảo”, “Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”, “Giáo trình phục vụ học phần Đại số”),
("entity", “tài liệu tham khảo”, “Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004”, “Giáo trình phục vụ học phần Đại số”),
("entity", “tài liệu tham khảo thêm”, “Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”, “Giáo trình tiếng Anh phục vụ học phần Đại số”),
("entity", “tài liệu tham khảo thêm”, “Elementary Linear Algebra, 11th- edition. Wiley, 2013”, “Giáo trình tiếng Anh phục vụ học phần Đại số”),
("entity", “tác giả ”, “Nguyễn Đình Trí”, “Tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”),
("entity", “tác giả ”, “Lê Trọng Vinh”, “Tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”),
("entity", “tác giả ”, “Dương Thuỷ Vĩ”, “Tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”),
("entity", “tác giả ”, “Nguyễn Hữu Việt Hưng”, “Tác giả của cuốn Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004”),
("entity", “tác giả ”, “Ron Lardson”, “Tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”),
("entity", “tác giả ”, “Edward”, “Tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”),
("entity", “tác giả ”, “Falvo”, “Tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”),
("entity", “tác giả ”, “Anton Rorres”, “Tác giả của cuốn Elementary Linear Algebra, 11th- edition. Wiley, 2013”),
("relationship", "Đại số", “Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”, "Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007 là tài liệu tham khảo cho học phần Đại số”, “tài liệu tham khảo, tltk, học phần, môn học”),
("relationship", "Đại số", “Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004”, "Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004 là tài liệu tham khảo cho học phần Đại số”, “tài liệu tham khảo, tltk, học phần, môn học”),
("relationship", "Đại số", “Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”, "Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009 là tài liệu tham khảo thêm cho học phần Đại số”, “tài liệu tham khảo, tltk, tài liệu tham khảo thêm, học phần, môn học”),
("relationship", "Đại số", “Elementary Linear Algebra, 11th- edition. Wiley, 2013”, "Elementary Linear Algebra, 11th- edition. Wiley, 2013 là tài liệu tham khảo thêm cho học phần Đại số”, “tài liệu tham khảo, tltk, tài liệu tham khảo thêm, học phần, môn học”),
("relationship", "Nguyễn Đình Trí”, "Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007", “Nguyễn Đình Trí là đồng tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Lê Trọng Vinh”, "Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007", “Lê Trọng Vinh là đồng tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Dương Thuỷ Vĩ”, "Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007", “Dương Thuỷ Vĩ là đồng tác giả của cuốn Giáo trình toán học cao cấp tập 1. NXB Giáo dục, 2007”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Nguyễn Hữu Việt Hưng”, "Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004", “Nguyễn Hữu Việt Hưng là tác giả của cuốn Đại số tuyến tính. NXB Đại học Quốc gia Hà Nội. Tái bản lần 2, 2004”, “tác giả, giáo trình, sách”),
("relationship", "Ron Lardson”, "Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009", “Ron Lardson là đồng tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Edward”, "Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009", “Edward là đồng tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Falvo”, "Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009", “Falvo là đồng tác giả của cuốn Elementary Linear Algebra, 6th- edition. Houghton Mifflin Hartcourt Publising Company, 2009”, “tác giả, đồng tác giả, giáo trình, sách”),
("relationship", "Anton Rorres”, "Tác giả của cuốn Elementary Linear Algebra, 11th- edition. Wiley, 2013", “Anton Rorres là tác giả của cuốn Tác giả của cuốn Elementary Linear Algebra, 11th- edition. Wiley, 2013”, “tác giả, giáo trình, sách”)
]
"""


PROMPT["EXTRACT_ENTITY_RELATIONSHIP"] = """

This in the input text: {input_text}

"""

PROMPT["CHAT"] = """
{question}

{received}
"""

PROMPT["RELATIONSHIP_POLLING"] = """
Dịch sang tiếng Việt:

Thực hiện các bước sau:

0. Không viết bất kỳ đoạn mã nào.
1. Xác định tất cả các thực thể và phân loại chúng thành ngành đào tạo, giảng viên, môn học,...
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì, từ thuộc về, hiểu, sử dụng, liên quan tới...
3. Trả kết quả dưới dạng ("entity", "loại", "Tên", "mô tả") cho loại thực thể hoặc ("relationship", "Nút 1", "Nút 2", "mô tả", "từ khóa") cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu với "entity" hoặc "relationship".
4. Giảm thiểu số lượng thực thể không có mối quan hệ.

Ví dụ:

Đầu vào:
[
("entity", "người", "Alex", "Alex là một nhân vật trải nghiệm sự thất vọng và quan sát sự tương tác giữa các nhân vật khác."),
("entity", "người", "Taylor", "Taylor được miêu tả với sự tự tin độc đoán và có một khoảnh khắc tôn kính một thiết bị, cho thấy sự thay đổi quan điểm.")
]

Đầu ra:
[
("relationship", "Alex", "các nhân vật khác", "Alex là một nhân vật trải nghiệm sự thất vọng và quan sát sự tương tác giữa các nhân vật khác.", "trải nghiệm")
]

Sẽ cung cấp cho bạn một danh sách các mối quan hệ, bạn có thể tìm thêm các thực thể/mối quan hệ từ đó.

Đây là danh sách các thực thể:
{relationships}

"""

PROMPT["ENTITY_POLLING"] = """
Thực hiện các bước sau:

0. Không viết bất kỳ đoạn mã nào.
1. Xác định tất cả các thực thể và phân loại chúng thành ngành đào tạo, giảng viên, môn học...
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì, từ thuộc về, hiểu, sử dụng, liên quan tới...
3. Trả kết quả dưới dạng ("entity", "loại", "Tên", "mô tả") cho loại thực thể hoặc ("relationship", "Nút 1", "Nút 2", "mô tả", "từ khóa") cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu với "entity" hoặc "relationship".
4. Tạo thêm các thực thể
Ví dụ:

Đầu vào:
[
("relationship", "Toán học rời rạc", “CLO1”, “CLO1 là hiểu được các khái niệm cơ bản về tư duy logic các phương pháp toán trên tập các đối tượng rời rạc các lược đồ xây dựng thuật toán", “đầu ra, kiến thức, học phần”),
("relationship", "Toán học rời rạc", “CLO2”, “CLO2 là hiểu và vận dụng được các kiến thức cơ bản của lý thuyết đồ thị”, “đầu ra, kiến thức, học phần”),
]

Đầu ra:
[
("entity", "Kiến thức", "khái niệm cơ bản về tư duy logic", "chuẩn đầu ra kiến thức của CLO1", "chuẩn đầu ra, kiến thức, toán rời rạc")
("entity", "Kiến thức", "phương pháp toán trên tập các đối tượng rời rạc", "chuẩn đầu ra kiến thức của CLO1", "chuẩn đầu ra, kiến thức, toán rời rạc")
("entity", "Kiến thức", "lược đồ xây dựng thuật toán", "chuẩn đầu ra kiến thức của CLO1", "chuẩn đầu ra, kiến thức, toán rời rạc")
("entity", "Kiến thức", "lý thuyết đồ thị", "chuẩn đầu ra kiến thức của CLO2", "chuẩn đầu ra, kiến thức, toán rời rạc")
]


Sẽ cung cấp cho bạn một danh sách các thực thể, bạn có thể tìm thêm các thực thể/mối quan hệ từ đó.

Đây là danh sách các mối quan hệ:
{entities}

"""

PROMPT["EXTRACT_ENTITY_CHAT"] = """
Thực hiện các bước sau:

0. Không viết mã.
1. Một thực thể là một danh từ đại diện cho một ngành đào tạo, giảng viên, môn học, địa điểm, sách, giáo trình.... Tìm tất cả các thực thể có thuộc tính đó.
2. Nếu câu hỏi là về ngành đào tạo, giảng viên, môn học, địa điểm, sách, giáo trình....
3. Trả về đầu ra là "entity", ... hoặc "type", ...

Ví dụ 1:
Câu hỏi:

Nguyễn Ngọc Hoá là ai?

Đầu ra:
[
("entity", "người", "Nguyễn Ngọc Hoá"),
("type", "người"),
]

Ví dụ 2:

Câu hỏi:
Liệt kê tất cả các giảng viên có học hàm, học vị từ Phó giáo sư trở lên?

Đầu ra:
[
("type", "PGS. TS"),
("type", "người"),
("type", "giảng viên"),
("type", "học hàm"),
]

Đây là câu hỏi:
{question}
"""


PROMPT_EN: dict[str, str] = {}

PROMPT_EN["SYSTEM_INTRUCT"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, .... Get it description and important keyword.
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, a componenet of, ...
3. Return it as in the format of ("entity", "type", "name", "description") for the entity type or ("relationship", "Node 1", "Node 2", "description", "keyword") the relationship type. Don't give any empty output. It always started with either "entity" or "relationship"

For example:
With this input:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
The output should be:
[
("entity", "person", "Alex", "Alex is a character who experiences frustration and is observant of the dynamics among other characters."),
("entity", "person", "Taylor", "Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."),
("entity", "person", "Jordan", "Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."),
("entity", "person","Cruz","Cruz is associated with a vision of control and order, influencing the dynamics among other characters."),
("entity", "technology","The Device", "The Device is central to the story, with potential game-changing implications, and is revered by Taylor.")
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
("relationship","Taylor","Jordan", "Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce.","conflict resolution, mutual respect"),
("relationship","Jordan","Cruz","Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order.","ideological conflict, rebellion"),
("relationship", "Taylor", "The Device", "Taylor shows reverence towards the device, indicating its importance and potential impact.","reverence, technological significance"),
]
"""

PROMPT_EN["EXTRACT_ENTITY_RELATIONSHIP"] = """

This in the input text: {input_text}

"""

PROMPT_EN["CHAT"] = """
You will be provided with a list of information. Your task is to accurately answer a question based solely on the information given.

Information:
{received}

Answer this question:
{question}

"""

PROMPT_EN["RELATIONSHIP_POLLING"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, ...
3. Return it as in the format of ("entity", "type", "name", "description") for the entity type or ("relationship", "Node 1", "Node 2", "description", "keyword") the relationship type. Don't give any empty output. It always started with either "entity" or "relationship"
4. Minimize amount of entities that don't have any relattionship.

Example:
Input:
[
("entity", "person", "Alex", "Alex is a character who experiences frustration and is observant of the dynamics among other characters."),
("entity", "person", "Taylor", "Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."),
]

Output:
[
("relationship", "Alex", "other characters", "Alex is a character who experiences frustration and is observant of the dynamics among other characters.", "experiences experiences"),
]


Will provide you a list of relationships can you find additional entities / relationships from that
This is the this of relationships
{relationships}

"""

PROMPT_EN["ENTITY_POLLING"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, ...
3. Return it as in the format of ("entity", "type", "name", "description") for the entity type or ("relationship", "Node 1", "Node 2", "description", "keyword") the relationship type. Don't give any empty output. It always started with either "entity" or "relationship"
4. Minimize amount of entities that don't have any relattionship.

Example:
Input:
[
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
]

Output:
("entity", "Person" "Alex", "Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("entity", "Concept", "Cruz's vision", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),

Will provide you a list of entities can you find additional entities / relationships from that
This is the this of relationships
{entities}

"""

PROMPT_EN["EXTRACT_ENTITY_CHAT"] = """
Do the following:
0. Don't write any code.
1. An entity is an noun which represent a location, organization, person, geo or event, .... Find all entities, that have that propertity.
2. If the quesiton is about location, organization, person, geo or event, .... 
3. Return the output of is either  ("entity", ...) or ("type", ... )

Example 1:

Question:

Who is Alex?

Output:
[
("entity", "person", "Alex"),
]

Example 2:

Question:

Tell me about any orginization in the document?

Output:
[
("type", "Orginization"),
]

This is the question:
{question}
"""

