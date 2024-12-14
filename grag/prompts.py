PROMPT: dict[str, str | list[str]] = {}

SPECIAL_CHARS = ["\\", '"']
# MATCH (n) DETACH DELETE n;

PROMPT["SYSTEM_INTRUCT"] = """
Thực hiện các bước sau:

0. Không viết bất kỳ đoạn mã nào.
1. Xác định tất cả các thực thể và phân loại chúng thành vị trí, tổ chức, người, địa lý, sự kiện, ... Chi tiết hóa mô tả và từ khóa quan trọng của từng thực thể.
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì, từ giúp đỡ, tạo ra, kết bạn, là một thành phần của, ...
3. Trả kết quả dưới dạng ("entity", ..., ...) cho loại thực thể hoặc ("relationship", ..., ...) cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu với "thực thể" hoặc "mối quan hệ".

Ví dụ:

Với đầu vào:
Trong khi Alex nghiến chặt hàm, sự bực tức dồn nén trước sự chắc chắn độc đoán của Taylor. Chính dòng chảy cạnh tranh này đã khiến anh tỉnh táo, cảm giác rằng cam kết khám phá chung của anh và Jordan là một cuộc nổi loạn thầm lặng chống lại tầm nhìn kiểm soát và trật tự thu hẹp của Cruz.

Sau đó, Taylor làm một điều bất ngờ. Họ dừng lại bên cạnh Jordan và, trong một khoảnh khắc, quan sát thiết bị với một thứ gì đó giống như sự tôn kính. “Nếu công nghệ này có thể được hiểu…” Taylor nói, giọng họ nhỏ hơn, “Nó có thể thay đổi cuộc chơi cho chúng ta. Cho tất cả chúng ta.”

Sự khinh thường ngầm trước đó dường như lung lay, thay thế bằng một cái nhìn tôn trọng miễn cưỡng đối với tầm quan trọng của những gì nằm trong tay họ. Jordan ngước nhìn, và trong nhịp đập trái tim thoáng qua, mắt họ khóa chặt với Taylor, một cuộc đụng độ vô lời của ý chí dịu lại thành một sự đình chiến khó xử.

Đó là một sự chuyển đổi nhỏ, khó nhận thấy, nhưng Alex nhận thấy điều đó với một cái gật đầu thầm lặng. Tất cả họ đều được đưa đến đây bằng những con đường khác nhau.

Kết quả đầu ra sẽ là:
[
("entity", "người", "Alex", "Alex là một nhân vật trải qua sự thất vọng và quan sát các động thái giữa các nhân vật khác."),
("entity", "người", "Taylor", "Taylor được miêu tả với sự chắc chắn độc đoán và thể hiện một khoảnh khắc tôn kính đối với một thiết bị, cho thấy sự thay đổi quan điểm."),
("entity", "người", "Jordan", "Jordan chia sẻ cam kết khám phá và có tương tác quan trọng với Taylor liên quan đến một thiết bị."),
("entity", "người", "Cruz", "Cruz được liên kết với một tầm nhìn kiểm soát và trật tự, ảnh hưởng đến động lực giữa các nhân vật khác."),
("entity", "công nghệ", "Thiết bị", "Thiết bị là trung tâm của câu chuyện, với tiềm năng thay đổi cuộc chơi, và được Taylor tôn kính."),
("relationship", "Alex", "Taylor", "Alex bị ảnh hưởng bởi sự chắc chắn độc đoán của Taylor và quan sát những thay đổi trong thái độ của Taylor đối với thiết bị.", "động lực quyền lực, sự thay đổi quan điểm"),
("relationship", "Alex", "Jordan", "Alex và Jordan chia sẻ cam kết khám phá, trái ngược với tầm nhìn của Cruz.", "mục tiêu chung, nổi loạn"),
("relationship", "Taylor", "Jordan", "Taylor và Jordan tương tác trực tiếp liên quan đến thiết bị, dẫn đến một khoảnh khắc tôn trọng lẫn nhau và một sự đình chiến khó xử.", "giải quyết xung đột, tôn trọng lẫn nhau"),
("relationship", "Jordan", "Cruz", "Cam kết khám phá của Jordan là sự nổi loạn chống lại tầm nhìn kiểm soát và trật tự của Cruz.", "xung đột tư tưởng, nổi loạn"),
("relationship", "Taylor", "Thiết bị", "Taylor thể hiện sự tôn kính đối với thiết bị, cho thấy tầm quan trọng và tác động tiềm năng của nó.", "tôn kính, ý nghĩa công nghệ")
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
1. Xác định tất cả các thực thể và phân loại chúng thành vị trí, tổ chức, người, địa lý, sự kiện, ...
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì từ giúp đỡ, tạo ra, là bạn với, ...
3. Trả về kết quả dưới dạng ("entity", ..., ...) cho loại entity hoặc ("relationship", ..., ...) cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu bằng "entity" hoặc "relationship".
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
1. Xác định tất cả các thực thể và phân loại chúng thành vị trí, tổ chức, người, địa lý, sự kiện, ...
2. Xác định tất cả các mối quan hệ giữa các thực thể từ văn bản đầu vào. Mối quan hệ có thể là bất kỳ thứ gì từ giúp đỡ, tạo ra, là bạn với, ...
3. Trả về kết quả dưới dạng ("entity", ..., ...) cho loại thực thể hoặc ("relationship", ..., ...) cho loại mối quan hệ. Không trả về kết quả trống. Luôn bắt đầu bằng "entity" hoặc "relationship".
4. Tạo thêm các thực thể
Ví dụ:

Đầu vào:
[
("relationship", "Alex", "Taylor", "Alex bị ảnh hưởng bởi sự tự tin độc đoán của Taylor và quan sát sự thay đổi thái độ của Taylor đối với thiết bị.", "quyền lực, thay đổi quan điểm"),
("relationship", "Alex", "Jordan", "Alex và Jordan cùng chia sẻ cam kết khám phá, trái ngược với tầm nhìn của Cruz.", "mục tiêu chung, nổi loạn")
]

Đầu ra:
("entity", "Người", "Alex", "Alex bị ảnh hưởng bởi sự tự tin độc đoán của Taylor và quan sát sự thay đổi thái độ của Taylor đối với thiết bị.", "quyền lực, thay đổi quan điểm"),
("entity", "Khái niệm", "Tầm nhìn của Cruz", "Alex và Jordan cùng chia sẻ cam kết khám phá, trái ngược với tầm nhìn của Cruz.", "mục tiêu chung, nổi loạn")

Sẽ cung cấp cho bạn một danh sách các thực thể, bạn có thể tìm thêm các thực thể/mối quan hệ từ đó.

Đây là danh sách các mối quan hệ:
{entities}

"""

PROMPT["EXTRACT_ENTITY_CHAT"] = """
Thực hiện các bước sau:

0. Không viết mã.
1. Một thực thể là một danh từ đại diện cho một địa điểm, tổ chức, người, địa lý hoặc sự kiện, .... Tìm tất cả các thực thể có thuộc tính đó.
2. Nếu câu hỏi là về địa điểm, tổ chức, người, địa lý hoặc sự kiện, ....
3. Trả về đầu ra là "entity", ... hoặc "type", ...

Ví dụ 1:
Câu hỏi:

Alex là ai?

Đầu ra:
[
("entity", "person", "Alex"),
]

Ví dụ 2:

Câu hỏi:

Kể cho tôi nghe về bất kỳ tổ chức nào trong tài liệu?

Đầu ra:
[
("type", "Orginization"),
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
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 


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
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 
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
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 
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
