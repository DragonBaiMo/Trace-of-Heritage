"""演示数据种子脚本，插入截图所需的样本数据。"""
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加 backend 目录到 PATH
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.resource import Resource, ResourceGeoTrail
from app.models.product import Product, UserPoint
from app.models.wiki import WikiEntry
from app.models.cultural import VideoRecommendation, WeeklyDigest

def seed():
    db = SessionLocal()
    try:
        # 获取 admin 用户 id
        from app.models.user import User
        admin = db.query(User).filter(User.role == "admin").first()
        user = db.query(User).filter(User.username == "heritage_user").first()
        if not admin:
            print("管理员用户不存在，请先确保后端已启动并初始化")
            return
        if not user:
            print("heritage_user 不存在")
            return

        # ---- 插入资源 ----
        existing = db.query(Resource).count()
        if existing == 0:
            resources_data = [
                dict(title="《霸王别姬》精华折子", resource_type="video", synopsis="梅派经典剧目，展现虞姬告别霸王的悲壮情怀，唱腔委婉动人。", tags=["京剧", "梅派", "经典"], genre="京剧", region_code="CN-BJ", author="梅兰芳", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="《牡丹亭·游园惊梦》", resource_type="video", synopsis="汤显祖传世名作，杜丽娘游园寻梦，昆曲唱腔婉转悠扬。", tags=["昆曲", "传统", "UNESCO"], genre="昆曲", region_code="CN-JS", author="白先勇", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="陕西皮影戏表演集锦", resource_type="video", synopsis="陕西皮影戏非物质文化遗产展示，光影交错呈现传统技艺。", tags=["皮影戏", "非遗", "陕西"], genre="皮影戏", region_code="CN-SN", author="华县皮影剧团", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="《白蛇传》全本", resource_type="video", synopsis="越剧经典剧目，讲述白娘子与许仙凄美爱情故事。", tags=["越剧", "经典", "爱情"], genre="越剧", region_code="CN-ZJ", author="上海越剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="川剧变脸技艺解析", resource_type="article", synopsis="深度解析川剧变脸的历史渊源、技术原理与传承现状，附珍贵历史影像。", tags=["川剧", "变脸", "非遗"], genre="川剧", region_code="CN-SC", author="四川省川剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="昆曲身段基础教程", resource_type="article", synopsis="系统介绍昆曲表演中手眼身法步的基本规范，配有图解分析。", tags=["昆曲", "教程", "身法"], genre="昆曲", region_code="CN-JS", author="苏州昆剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="《贵妃醉酒》全场录像", resource_type="video", synopsis="梅派代表作，杨贵妃醉卧百花亭，水袖舞步精巧绝伦。", tags=["京剧", "梅派", "杨贵妃"], genre="京剧", region_code="CN-BJ", author="北京京剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="河南豫剧《花木兰》", resource_type="video", synopsis="豫剧经典剧目，展现花木兰代父从军的英雄气概，唱腔高亢激昂。", tags=["豫剧", "花木兰", "经典"], genre="豫剧", region_code="CN-HA", author="河南豫剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="粤剧《帝女花》选段", resource_type="video", synopsis="粤剧经典剧目，描写明末公主长平与周世显的爱情悲歌。", tags=["粤剧", "帝女花", "广东"], genre="粤剧", region_code="CN-GD", author="广州红豆粤剧团", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="黄梅戏《天仙配》", resource_type="video", synopsis="安徽黄梅戏代表剧目，七仙女与董永的浪漫传说。", tags=["黄梅戏", "天仙配", "安徽"], genre="黄梅戏", region_code="CN-AH", author="安徽省黄梅戏剧院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="京剧脸谱艺术图集", resource_type="image", synopsis="系统整理京剧脸谱色彩与图案含义，收录200余种经典脸谱图样。", tags=["京剧", "脸谱", "图集"], genre="京剧", region_code="CN-BJ", author="中国戏曲学院", copyright_status="public", status="approved", submitter_id=admin.id, reviewer_id=admin.id),
                dict(title="《秦香莲》全本录像", resource_type="video", synopsis="传统剧目，讲述陈世美忘恩负义，铡美案的历史典故。", tags=["京剧", "传统", "公正"], genre="京剧", region_code="CN-BJ", author="中国京剧院", copyright_status="public", status="pending", submitter_id=1, reviewer_id=None),
                dict(title="豫剧唱腔教学入门", resource_type="article", synopsis="为初学者设计的豫剧基础唱腔教学，包含发声训练与音阶练习。", tags=["豫剧", "教程", "唱腔"], genre="豫剧", region_code="CN-HA", author="河南豫剧传承中心", copyright_status="public", status="draft", submitter_id=1),
            ]
            for rd in resources_data:
                db.add(Resource(**rd))
            db.commit()
            print(f"已插入 {len(resources_data)} 条资源记录")

            # 为第一条资源添加地理轨迹
            res = db.query(Resource).filter(Resource.title == "《霸王别姬》精华折子").first()
            if res:
                trails = [
                    ResourceGeoTrail(resource_id=res.id, place_name="北京", longitude=116.4074, latitude=39.9042, order_no=1),
                    ResourceGeoTrail(resource_id=res.id, place_name="上海", longitude=121.4737, latitude=31.2304, order_no=2),
                    ResourceGeoTrail(resource_id=res.id, place_name="广州", longitude=113.2644, latitude=23.1291, order_no=3),
                ]
                for t in trails:
                    db.add(t)
                db.commit()
                print("已插入地理轨迹数据")
        else:
            print(f"资源表已有 {existing} 条数据，跳过")

        # ---- 插入商品 ----
        prod_count = db.query(Product).count()
        if prod_count == 0:
            products_data = [
                dict(title="京剧脸谱手绘套装", points_price=150, stock=50, status="active", cover=None),
                dict(title="昆曲折扇（桃花扇款）", points_price=200, stock=30, status="active", cover=None),
                dict(title="皮影戏人偶（武生款）", points_price=300, stock=20, status="active", cover=None),
                dict(title="非遗传承研学营门票", points_price=500, stock=10, status="active", cover=None),
                dict(title="戏曲艺术纪念邮票册", points_price=100, stock=100, status="active", cover=None),
                dict(title="变脸川剧主题文化衫", points_price=250, stock=40, status="active", cover=None),
                dict(title="越剧经典剧目全集DVD", points_price=180, stock=25, status="active", cover=None),
                dict(title="黄梅戏唱词精选图书", points_price=80, stock=60, status="active", cover=None),
                dict(title="戏曲文化主题背包", points_price=350, stock=15, status="active", cover=None),
                dict(title="梅兰芳纪念珍藏本", points_price=600, stock=5, status="active", cover=None),
            ]
            for pd in products_data:
                db.add(Product(**pd))
            db.commit()
            print(f"已插入 {len(products_data)} 条商品记录")
        else:
            print(f"商品表已有 {prod_count} 条数据，跳过")

        # ---- 给 heritage_user 添加积分 ----
        points_row = db.query(UserPoint).filter(UserPoint.user_id == user.id).first()
        if not points_row:
            db.add(UserPoint(user_id=user.id, balance=520))
            db.commit()
            print(f"已为 heritage_user 添加 520 积分")
        elif points_row.balance == 0:
            points_row.balance = 520
            db.commit()
            print(f"已将 heritage_user 积分更新为 520")
        else:
            print(f"heritage_user 当前积分: {points_row.balance}")

        print("\n种子数据插入完成！")

        # ---- 插入百科词条 ----
        wiki_count = db.query(WikiEntry).count()
        if wiki_count == 0:
            wiki_data = [
                # ===== genre（剧种）=====
                dict(
                    title="京剧",
                    category="genre",
                    status="approved",
                    content="""## 京剧

京剧，又称平剧、京戏，是中国戏曲中影响最大的剧种，被誉为"国剧"。形成于19世纪中叶的北京，以徽剧、汉剧为基础融合昆曲等多种声腔，集唱、念、做、打于一体。

### 历史渊源
1790年，四大徽班（三庆、四喜、春台、和春）相继进京，与汉调艺人合作，博采众长，最终形成了独特的京剧艺术体系。道光年间（1820—1850年）正式确立为独立剧种。

### 表演特色
- **唱腔**：分西皮、二黄两大声腔体系
- **行当**：生旦净末丑五大行当
- **伴奏**：以京胡、月琴、三弦为文场，锣鼓为武场
- **脸谱**：颜色含义鲜明，红忠白奸黑正直

### 代表剧目
《霸王别姬》《贵妃醉酒》《空城计》《铡美案》《龙凤呈祥》

### 非遗保护
2010年入选联合国教科文组织《人类非物质文化遗产代表作名录》。""",
                ),
                dict(
                    title="昆曲",
                    category="genre",
                    status="approved",
                    content="""## 昆曲

昆曲，又称昆剧，是中国最古老的剧种之一，发源于苏州昆山，被称为"百戏之祖"，距今已有600余年历史。

### 历史渊源
元末明初，昆山腔在苏州一带兴起。明嘉靖年间，魏良辅对昆腔进行改革，创制水磨腔，使昆曲声调更加圆润悠长。汤显祖的《牡丹亭》等传奇作品使昆曲达到鼎盛。

### 表演特色
- **水磨腔**：旋律婉转细腻，节奏徐缓
- **身段**：手眼身法步极为讲究，舞蹈性强
- **文辞**：曲文雅丽，文学价值极高
- **伴奏**：以曲笛为主，配合笙、箫、琵琶

### 代表剧目
《牡丹亭》《长生殿》《桃花扇》《西厢记》《浣纱记》

### 非遗保护
2001年入选联合国教科文组织首批《人类口头和非物质文化遗产代表作》。""",
                ),
                dict(
                    title="越剧",
                    category="genre",
                    status="approved",
                    content="""## 越剧

越剧，发源于浙江省绍兴市嵊州，是中国第二大剧种，以女子越剧为主要形式，擅长抒情，声腔柔美清丽。

### 历史渊源
越剧起源于清朝光绪年间浙江嵊州的落地唱书，约1906年登上戏台。20世纪30—40年代在上海发展壮大，女子越剧兴起，涌现出袁雪芬、傅全香等大师。

### 表演特色
- **唱腔**：流派纷呈，有袁派、尹派、傅派等十余个流派
- **表演**：细腻婉约，长于表现女性情感
- **服装**：古典华美，以软底靴、水袖为特色
- **题材**：多取材才子佳人故事

### 代表剧目
《梁山伯与祝英台》《红楼梦》《西厢记》《白蛇传》《祥林嫂》""",
                ),
                dict(
                    title="粤剧",
                    category="genre",
                    status="approved",
                    content="""## 粤剧

粤剧，又称广府大戏，是广东省地方传统戏曲，以粤语演唱，流行于广东、香港、澳门及海外华人社区，是海外影响力最大的中国戏曲剧种之一。

### 历史渊源
粤剧形成于明末清初，由外省戏班传入广东后与本地民间音乐融合发展而成，清末至民国年间达到鼎盛。

### 表演特色
- **唱腔**：梆黄为主，融合南音、粤讴等本土音乐
- **表演**：武打激烈，以高台功夫著称
- **服装**：华丽富贵，刺绣精美
- **语言**：以粤语演唱，另有戏棚官话传统

### 代表剧目
《帝女花》《紫钗记》《再世红梅记》《牡丹亭》《白蛇传》

### 非遗保护
2009年与粤曲一道入选联合国教科文组织《人类非物质文化遗产代表作名录》。""",
                ),
                dict(
                    title="黄梅戏",
                    category="genre",
                    status="approved",
                    content="""## 黄梅戏

黄梅戏，旧称采茶戏或黄梅调，发源于湖北黄梅县，流行于安徽、湖北、江西等地，以安徽安庆为中心发展壮大，是安徽省最具代表性的地方戏曲剧种。

### 历史渊源
黄梅戏起源于清末鄂、赣、皖三省交界地区的民间采茶歌舞，辛亥革命后逐渐流入安庆，在农村草台班中发展，20世纪50年代以《天仙配》等剧目蜚声全国。

### 表演特色
- **唱腔**：明快流畅，富有民歌风味，易于传唱
- **表演**：生活气息浓郁，朴实自然
- **语言**：以安庆方言为基础，吐字清晰
- **乐器**：高胡、二胡、扬琴配合锣鼓

### 代表剧目
《天仙配》《女驸马》《打猪草》《夫妻观灯》《牛郎织女》

### 代表艺术家
严凤英（首创黄梅戏女演员），王少舫，马兰，吴琼""",
                ),
                dict(
                    title="豫剧",
                    category="genre",
                    status="approved",
                    content="""## 豫剧

豫剧，又称河南梆子，是中国戏曲中观众数量最多的地方剧种之一，起源于河南，流行于河南及中原地区，以其高亢激昂、大气磅礴的唱腔著称。

### 历史渊源
豫剧形成于明末清初，由秦腔与蒲州梆子传入河南后与本地民间音乐融合，演变为具有中原特色的大型戏曲剧种，清代中期已遍布全省。

### 表演特色
- **唱腔**：梆子腔系，高亢激越，行腔自由奔放
- **流派**：祥符调（开封）、豫东调（商丘）、豫西调（洛阳）、沙河调（漯河）
- **题材**：历史故事、民间传说、现代生活均有涉及
- **伴奏**：板胡领奏，辅以二胡、月琴

### 代表剧目
《花木兰》《穆桂英挂帅》《朝阳沟》《七品芝麻官》《刘大哥讲话理太偏》

### 代表艺术家
常香玉（"豫剧皇后"）、陈素真、崔兰田、马金凤""",
                ),
                dict(
                    title="秦腔",
                    category="genre",
                    status="approved",
                    content="""## 秦腔

秦腔，又称梆子腔，是中国西北地区最古老、影响最大的地方戏曲剧种，流行于陕西、甘肃、宁夏、青海、新疆等地，被誉为"百戏之祖"之一，是梆子腔系的鼻祖。

### 历史渊源
秦腔起源于先秦时期的陕西民间，以木梆击节为特色，明代已形成较完整的声腔体系，清乾隆年间传入北京，对全国各地梆子腔系产生深远影响。

### 表演特色
- **唱腔**：以梆子击节，高亢激昂，苍劲豪迈
- **表演**：动作粗犷有力，武打火爆，善于表现英雄人物
- **特色绝技**：吹火、踩跷、耍帽翅
- **化妆**：简朴自然，侧重人物气质

### 代表剧目
《窦娥冤》《三滴血》《游西湖》《火焰驹》《赵氏孤儿》

### 代表艺术家
李正敏、刘毓中、肖若兰、王天民""",
                ),
                dict(
                    title="川剧",
                    category="genre",
                    status="approved",
                    content="""## 川剧

川剧，四川地方传统戏曲，融昆腔、高腔、胡琴、弹戏、灯腔五种声腔于一体，以独特的变脸、吐火技艺享誉世界，是四川省最具代表性的文化符号之一。

### 历史渊源
川剧形成于清代，由外来声腔在四川盆地与本土文化碰撞融合而成，18世纪末至19世纪初逐渐定型，成为西南最重要的地方剧种。

### 表演特色
- **变脸**：以特殊方式瞬间换脸，展现人物内心变化，为世界级绝技
- **吐火**：演员口吐火焰，增强舞台震撼效果
- **帮腔**：台下乐队帮腔演唱，烘托情绪
- **高腔**：无伴奏清唱，历史最悠久

### 代表剧目
《白蛇传》《柳荫记》《御河桥》《秋江》《拉郎配》

### 代表艺术家
阳友鹤、周慕莲、竞华、陈书舫""",
                ),
                dict(
                    title="评剧",
                    category="genre",
                    status="approved",
                    content="""## 评剧

评剧，是华北、东北地区广泛流行的地方戏曲，以口语化、生活化著称，题材贴近民间，唱词通俗易懂，曾被认为是"群众最喜爱的地方剧种之一"。

### 历史渊源
评剧起源于清末河北唐山一带的"蹦蹦戏"（莲花落），约1910年代正式命名为"评剧"，意为以演唱评说时事为主，20世纪50年代达到鼎盛。

### 表演特色
- **唱腔**：朴实自然，接近口语，曲调优美流畅
- **题材**：擅长表现现代生活，农村题材尤为突出
- **行当**：以花旦、青衣为主，生活气息浓厚
- **伴奏**：以板胡为主，配合扬琴、笛子

### 代表剧目
《刘巧儿》《花为媒》《杨三姐告状》《秦香莲》《小女婿》

### 代表艺术家
新凤霞（"评剧皇后"）、小白玉霜、赵丽蓉""",
                ),
                dict(
                    title="徽剧",
                    category="genre",
                    status="approved",
                    content="""## 徽剧

徽剧，安徽省地方戏曲，以皖南、皖中地区为主要流行区域，历史上曾风靡全国，是京剧的重要源头，素有"京剧之母"之称。

### 历史渊源
徽剧形成于明代末期安徽徽州、池州一带，清乾隆年间"四大徽班"进京，与其他声腔融合，最终催生了京剧。徽剧本身后来随着京剧的兴盛而逐渐式微。

### 表演特色
- **声腔**：二黄、西皮、昆腔、吹腔等多种声腔并存
- **武打**：以翻打扑跌见长，动作激烈
- **行当**：生旦净末丑俱全，文武兼备
- **服装**：古朴华丽，制作精良

### 代表剧目
《水淹七军》《闹天宫》《借东风》《群英会》《打金砖》

### 非遗保护
2006年入选首批国家级非物质文化遗产名录。""",
                ),
                # ===== figure（人物）=====
                dict(
                    title="梅兰芳",
                    category="figure",
                    status="approved",
                    content="""## 梅兰芳（1894—1961）

梅兰芳，名澜，字畹华，原籍江苏泰州，生于北京，是中国京剧史上最伟大的表演艺术家之一，京剧"四大名旦"之首，梅派旦角创始人。

### 艺术成就
梅兰芳在青衣、花旦的基础上，创立了以他名字命名的"梅派"，将京剧旦角艺术推向了空前高度。他的表演雍容华贵，端庄大方，唱腔甜润清丽，被誉为"梅腰""梅步""梅腔"。

### 代表剧目
《贵妃醉酒》《霸王别姬》《洛神》《西施》《天女散花》《嫦娥奔月》

### 国际影响
梅兰芳曾多次赴日本、美国、苏联访问演出，以精湛技艺打动西方观众，促进了中国传统文化的国际传播，被斯坦尼斯拉夫斯基赞誉为伟大的演员。

### 晚年贡献
建国后，梅兰芳历任中国京剧院院长、中国文联副主席，致力于京剧教育与传承。1961年病逝，举国同悲。""",
                ),
                dict(
                    title="程砚秋",
                    category="figure",
                    status="approved",
                    content="""## 程砚秋（1904—1958）

程砚秋，字御霜，满族，北京人，京剧"四大名旦"之一，程派旦角创始人，以幽咽婉转、深沉内敛的唱腔独树一帜，被称为"程腔"。

### 艺术成就
程砚秋幼年从师荣蝶仙，后得罗瘿公资助，拜梅兰芳为师。他刻苦钻研，突破传统，创立了以"程腔"为核心的程派艺术体系。程腔以低回婉转、若断若续为特点，极富感染力。

### 代表剧目
《锁麟囊》《春闺梦》《荒山泪》《碧玉簪》《窦娥冤》

### 艺术特色
- 嗓音略带沙哑，却化弱为强，形成独特程腔
- 水袖功夫精湛，长袖善舞
- 善于表现命运悲苦、心理复杂的女性角色

### 历史地位
程砚秋的程派旦角至今仍是京剧各流派中传承最为活跃的流派之一。""",
                ),
                dict(
                    title="荀慧生",
                    category="figure",
                    status="approved",
                    content="""## 荀慧生（1900—1968）

荀慧生，字慧声，艺名白牡丹，北京人，京剧"四大名旦"之一，荀派旦角创始人，以活泼热辣、妩媚多情的表演风格著称，人称"荀派活花旦"。

### 艺术成就
荀慧生幼习梆子，后改学京剧，博采众长，从梆子、河北梆子汲取营养，融入京剧花旦行当，创立了独具特色的荀派艺术。荀派表演活泼灵动，注重人物内心刻画。

### 代表剧目
《红娘》《荀灌娘》《钗头凤》《棒打薄情郎》《鱼藻宫》

### 艺术特色
- 唱腔俏丽甜润，节奏明快
- 表演灵活多变，善于刻画多情少女形象
- 身段潇洒自然，舞台感染力强

### 传承影响
荀派在当代依然活跃，北京京剧院等院团有专门的荀派传承梯队。""",
                ),
                dict(
                    title="马连良",
                    category="figure",
                    status="approved",
                    content="""## 马连良（1901—1966）

马连良，字温如，北京人，回族，是20世纪最负盛名的京剧老生演员，马派老生创始人，被誉为"马派"宗师，与梅兰芳并称"梅马"，堪称京剧艺术双峰。

### 艺术成就
马连良幼年入科，师从贾洪林，及长广泛学习各家之长，在谭派基础上大胆创新。马派老生以飘逸潇洒、圆润委婉的唱腔和洒脱利落的表演著称。

### 代表剧目
《借东风》《失空斩》（《失街亭》《空城计》《斩马谡》）《将相和》《四进士》《甘露寺》

### 艺术特色
- 唱腔圆润宽厚，韵味醇厚，行腔流畅自然
- 做工潇洒大方，表演具有名士风度
- 念白清晰悦耳，节奏鲜明

### 历史地位
马连良是"四大须生"（马谭杨奚）之首，影响了几代京剧老生演员。""",
                ),
                # ===== term（术语）=====
                dict(
                    title="生旦净末丑",
                    category="term",
                    status="approved",
                    content="""## 生旦净末丑

生旦净末丑，是中国传统戏曲（尤其是京剧）中对演员行当的总称，五大行当各有鲜明的人物类型与表演特色。

### 各行当解析

#### 生（shēng）
男性角色的总称。细分为：
- **老生**：中年以上男性，以须生为主，代表忠义正直
- **小生**：青年男性，风流俊雅
- **武生**：擅长武打的男性角色

#### 旦（dàn）
女性角色的总称。细分为：
- **青衣**（正旦）：端庄稳重的成年女性
- **花旦**：活泼灵巧的年轻女子
- **武旦**：擅长武打的女性角色
- **老旦**：老年女性角色
- **刀马旦**：骑马打仗的女性角色

#### 净（jìng）
俗称"花脸"，指性格刚烈、举止粗犷的男性角色。分铜锤花脸（唱功为主）和架子花脸（做功为主）两类。

#### 末（mò）
与老生相近，现多并入生行，指年龄较大、地位较低的男性角色。

#### 丑（chǒu）
喜剧角色，以白粉涂鼻为标志（小花脸），或扮演奸诈滑稽人物，或扮演机智幽默的小人物，是舞台上的活跃因子。""",
                ),
                dict(
                    title="唱念做打",
                    category="term",
                    status="approved",
                    content="""## 唱念做打

唱念做打，是中国传统戏曲表演艺术的"四功"，是戏曲演员必须掌握的基本功夫，也是评价戏曲表演水平的核心标准。

### 四功详解

#### 唱（chàng）——歌唱
指演员的演唱技艺，包括发声、行腔、韵味等。要求字正腔圆、运气自如，不同流派有各自独特的唱腔风格。

#### 念（niàn）——念白
指演员的台词道白，包括韵白（文雅的念白）和口白（接近日常语言的念白）。好的念白应字句清晰，节奏有致，富有音乐感。

#### 做（zuò）——表演动作
指演员的形体表演，包括手势（云手、兰花指）、眼神（眼功）、身段、步法等。"做"要求举手投足间都有章法，动作优美协调。

#### 打（dǎ）——武打
指演员的武打技艺，包括翻滚、对打、器械等。要求动作矫健、整齐一致，兼顾美观与技巧。

### 五法
与四功相配套的是五法：手（手势）、眼（眼神）、身（身体动作）、法（规矩法度）、步（步法），二者共同构成戏曲表演的完整规范体系。""",
                ),
                dict(
                    title="脸谱",
                    category="term",
                    status="approved",
                    content="""## 脸谱

脸谱，是中国京剧及其他地方戏曲中净行和丑行演员脸部特有的化妆艺术，以不同色彩和图案区分人物性格、身份与命运，是中国传统文化的重要符号。

### 颜色含义

| 颜色 | 象征含义 | 代表人物 |
|------|---------|---------|
| **红色** | 忠义、勇猛、正直 | 关羽、赵匡胤 |
| **黑色** | 刚正、勇猛、豪迈 | 包拯、张飞 |
| **白色** | 阴险奸诈、多谋善变 | 曹操、严嵩 |
| **蓝色** | 勇猛、桀骜、性格刚烈 | 窦尔敦、马武 |
| **绿色** | 骁勇、鲁莽 | 程咬金、武天虬 |
| **黄色** | 凶猛残暴或骁勇 | 宇文成都、典韦 |
| **金/银** | 神怪仙佛 | 孙悟空、哪吒 |
| **紫色** | 刚正威严 | 廉颇、徐延昭 |

### 图案类型
- **整脸**：整张脸用一种颜色为主，再加图案
- **三块瓦脸**：以额头、两颊分三块为主要形式
- **花三块瓦脸**：三块瓦脸加复杂纹饰
- **碎花脸**：图案繁复，多用于妖邪角色
- **歪脸**：五官歪斜，表示奸邪

### 文化价值
脸谱已成为中国传统文化的代表性视觉符号，广泛应用于工艺品、服装、邮票等领域。""",
                ),
                dict(
                    title="水袖",
                    category="term",
                    status="approved",
                    content="""## 水袖

水袖，是中国戏曲中旦角、生角演员在服装袖口处所附的白色绸缎长袖，因形似水波流动而得名，是戏曲表演中最具表现力的肢体语言工具之一。

### 基本特征
水袖以柔软白色绸缎制成，长约60—90厘米，缝缀于服装袖口，演员通过手腕、手臂的运动带动水袖产生各种形态。

### 主要技法

| 技法 | 动作说明 |
|------|---------|
| **抖袖** | 快速抖动手腕，水袖微颤 |
| **扬袖** | 向上抛起水袖 |
| **甩袖** | 向外横甩 |
| **卷袖** | 将水袖卷入手中 |
| **掷袖** | 用力抛出 |

### 表演意义
水袖的运用可以表达喜怒哀乐等多种情绪：
- 轻柔舒展——表示愉快、喜悦
- 快速翻腾——表示激动、愤怒
- 缓慢垂落——表示悲伤、失落

### 著名水袖表演
梅兰芳的水袖表演被誉为"梅袖"，成为旦角水袖功夫的最高标准。""",
                ),
            ]
            for wd in wiki_data:
                db.add(WikiEntry(**wd))
            db.commit()
            print(f"已插入 {len(wiki_data)} 条百科词条")
        else:
            print(f"百科表已有 {wiki_count} 条数据，跳过")

        # ---- 插入视频推荐 ----
        video_count = db.query(VideoRecommendation).count()
        if video_count == 0:
            video_data = [
                dict(
                    title="【京剧经典】梅兰芳《贵妃醉酒》全本",
                    description="梅派代表作，梅兰芳大师饰杨贵妃，水袖舞步精巧绝伦，唱腔甜润，是京剧旦角艺术的巅峰之作。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=梅兰芳+贵妃醉酒",
                    thumbnail_url=None,
                    opera_genre="京剧",
                    duration_display="45:12",
                    is_active=True,
                ),
                dict(
                    title="【昆曲·青春版】《牡丹亭·游园惊梦》",
                    description="白先勇监制青春版牡丹亭，两岸三地名角联袂，水磨腔婉转悠扬，获誉国际。杜丽娘游园一折尤为精彩。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=青春版+牡丹亭+游园惊梦",
                    thumbnail_url=None,
                    opera_genre="昆曲",
                    duration_display="52:30",
                    is_active=True,
                ),
                dict(
                    title="【越剧】《梁山伯与祝英台》经典全本",
                    description="越剧最广为人知的剧目，化蝶一折催人泪下。上海越剧院经典版本，唱腔柔美细腻。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=越剧+梁山伯与祝英台+全本",
                    thumbnail_url=None,
                    opera_genre="越剧",
                    duration_display="1:38:00",
                    is_active=True,
                ),
                dict(
                    title="【粤剧】《帝女花》选段合集",
                    description="粤剧经典中的经典，明末公主长平与周世显的爱情悲歌。香港名家演绎，粤语唱腔典雅婉约。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=粤剧+帝女花",
                    thumbnail_url=None,
                    opera_genre="粤剧",
                    duration_display="28:45",
                    is_active=True,
                ),
                dict(
                    title="【黄梅戏】严凤英《天仙配·树上鸟儿成双对》",
                    description="黄梅戏宗师严凤英演绎的《天仙配》，朴实清新，旋律优美，是中国最耳熟能详的戏曲唱段之一。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=严凤英+天仙配+树上鸟儿",
                    thumbnail_url=None,
                    opera_genre="黄梅戏",
                    duration_display="8:20",
                    is_active=True,
                ),
                dict(
                    title="【豫剧】常香玉《花木兰·谁说女子不如男》",
                    description="豫剧皇后常香玉饰演花木兰，高亢激昂的豫剧唱腔令人振奋。这段\"谁说女子不如男\"已成跨时代的文化符号。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=常香玉+花木兰+谁说女子不如男",
                    thumbnail_url=None,
                    opera_genre="豫剧",
                    duration_display="6:48",
                    is_active=True,
                ),
                dict(
                    title="【川剧】变脸绝技大全——世界级非遗技艺",
                    description="川剧变脸技艺纪录片，从历史渊源到技法揭秘，全面展示这一让全世界惊叹的中国绝活。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=川剧+变脸+技艺",
                    thumbnail_url=None,
                    opera_genre="川剧",
                    duration_display="22:15",
                    is_active=True,
                ),
                dict(
                    title="【秦腔】《窦娥冤·滚绣球》经典唱段",
                    description="秦腔高亢苍劲的嗓音，演绎窦娥冤的旷世悲愤。西北大地的古老呐喊，震撼人心。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=秦腔+窦娥冤+滚绣球",
                    thumbnail_url=None,
                    opera_genre="秦腔",
                    duration_display="12:30",
                    is_active=True,
                ),
                dict(
                    title="【评剧】新凤霞《刘巧儿》全剧",
                    description="评剧皇后新凤霞主演，取材真实案件改编，1956年拍摄的经典电影版本，感人至深，是中国戏曲电影的瑰宝。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=新凤霞+刘巧儿+评剧",
                    thumbnail_url=None,
                    opera_genre="评剧",
                    duration_display="1:12:00",
                    is_active=True,
                ),
                dict(
                    title="【京剧·入门】脸谱艺术与行当介绍",
                    description="专为初学者设计的京剧入门视频，用生动有趣的方式介绍生旦净末丑五大行当与脸谱颜色含义，老少皆宜。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=京剧+脸谱+行当+入门",
                    thumbnail_url=None,
                    opera_genre="京剧",
                    duration_display="18:40",
                    is_active=True,
                ),
                dict(
                    title="【昆曲】身段·水袖功夫教学示范",
                    description="苏州昆剧院名角示范昆曲基本身段与水袖技法，详细讲解手眼身法步的规范动作，适合爱好者学习。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=昆曲+水袖+教学",
                    thumbnail_url=None,
                    opera_genre="昆曲",
                    duration_display="35:00",
                    is_active=True,
                ),
                dict(
                    title="【纪录片】中国戏曲·百年传承",
                    description="CCTV出品纪录片，讲述20世纪以来中国戏曲的起伏兴衰、大师风范与新时代传承努力，史料珍贵，感人至深。",
                    platform="bilibili",
                    url="https://search.bilibili.com/all?keyword=中国戏曲+百年传承+纪录片",
                    thumbnail_url=None,
                    opera_genre=None,
                    duration_display="1:20:00",
                    is_active=True,
                ),
            ]
            for vd in video_data:
                db.add(VideoRecommendation(**vd))
            db.commit()
            print(f"已插入 {len(video_data)} 条视频推荐")
        else:
            print(f"视频推荐表已有 {video_count} 条数据，跳过")

        # ---- 插入每周荐读 ----
        digest_count = db.query(WeeklyDigest).count()
        if digest_count == 0:
            digests_data = [
                dict(
                    year=2026, week_number=15,
                    title="第15周荐读：昆曲·六百年的回响",
                    summary="本周精选昆曲文化相关的精彩内容，从历史传承到当代创新，感受"百戏之祖"的魅力。",
                    items_json=json.dumps([
                        {"title": "白先勇：为何要用一生守护昆曲？", "url": "https://search.bilibili.com/all?keyword=白先勇+昆曲", "type": "video", "desc": "白先勇详述青春版《牡丹亭》的创作初心"},
                        {"title": "《昆曲六百年》——从吴中水磨到世界非遗", "url": "https://search.bilibili.com/all?keyword=昆曲六百年+历史", "type": "video", "desc": "昆曲历史发展全景纪录"},
                        {"title": "苏州昆剧院：如何让年轻人爱上昆曲", "url": "https://search.bilibili.com/all?keyword=苏州昆剧院+年轻人+昆曲", "type": "video", "desc": "当代昆曲传承探索与实践"},
                        {"title": "昆曲经典折子戏精选：《游园惊梦》《拾画叫画》《痴梦》", "url": "https://search.bilibili.com/all?keyword=昆曲+折子戏+精选", "type": "video", "desc": "三折经典，感受昆曲之美"},
                    ], ensure_ascii=False),
                    published_at=datetime(2026, 4, 7),
                    is_published=True,
                ),
                dict(
                    year=2026, week_number=14,
                    title="第14周荐读：脸谱艺术——色彩与人性的交汇",
                    summary="探索京剧脸谱背后的美学密码，每一笔勾勒都是对人物灵魂的诠释。",
                    items_json=json.dumps([
                        {"title": "京剧脸谱的颜色密码：一图读懂200种脸谱", "url": "https://search.bilibili.com/all?keyword=京剧脸谱+颜色+含义", "type": "video", "desc": "趣味解读脸谱色彩象征体系"},
                        {"title": "脸谱制作工艺：从泥坯到艺术品", "url": "https://search.bilibili.com/all?keyword=京剧脸谱+手工+制作", "type": "video", "desc": "非遗传承人演示脸谱手工彩绘全程"},
                        {"title": "净行大师尚长荣：谈脸谱与人物塑造", "url": "https://search.bilibili.com/all?keyword=尚长荣+脸谱+净行", "type": "video", "desc": "国宝级艺术家分享脸谱美学心得"},
                        {"title": "【动画】小朋友学京剧：脸谱篇", "url": "https://search.bilibili.com/all?keyword=儿童+京剧+脸谱+动画", "type": "video", "desc": "生动有趣，适合亲子共赏"},
                    ], ensure_ascii=False),
                    published_at=datetime(2026, 3, 31),
                    is_published=True,
                ),
                dict(
                    year=2026, week_number=13,
                    title="第13周荐读：戏曲之声——唱腔流派大赏",
                    summary="梅尚程荀、马谭杨奚，品味京剧各大流派的独特腔韵，感受百花齐放的戏曲艺术。",
                    items_json=json.dumps([
                        {"title": "梅派、程派、荀派、尚派：四大名旦唱腔对比赏析", "url": "https://search.bilibili.com/all?keyword=四大名旦+唱腔+对比", "type": "video", "desc": "专业分析四大旦角流派风格差异"},
                        {"title": "程砚秋《锁麟囊·春秋亭》——程腔之美", "url": "https://search.bilibili.com/all?keyword=程砚秋+锁麟囊+春秋亭", "type": "video", "desc": "程派代表唱段，幽咽婉转令人沉醉"},
                        {"title": "马连良《借东风》——老生飘逸之风", "url": "https://search.bilibili.com/all?keyword=马连良+借东风", "type": "video", "desc": "马派老生标志性剧目"},
                        {"title": "《中国戏曲大师》系列讲座：流派的形成与传承", "url": "https://search.bilibili.com/all?keyword=中国戏曲+大师+流派+讲座", "type": "video", "desc": "学术视角解读戏曲流派文化"},
                    ], ensure_ascii=False),
                    published_at=datetime(2026, 3, 24),
                    is_published=True,
                ),
                dict(
                    year=2026, week_number=12,
                    title="第12周荐读：地方戏曲巡礼",
                    summary="从中原豫剧到西北秦腔，从巴蜀川剧到岭南粤剧，中华大地上百花争艳的地方戏曲文化。",
                    items_json=json.dumps([
                        {"title": "豫剧《朝阳沟》：一部戏改变了一个省的戏曲史", "url": "https://search.bilibili.com/all?keyword=豫剧+朝阳沟+经典", "type": "video", "desc": "豫剧现代戏里程碑之作"},
                        {"title": "秦腔·关中大地的天籁：《三滴血》片段", "url": "https://search.bilibili.com/all?keyword=秦腔+三滴血", "type": "video", "desc": "西北风情，苍劲雄浑"},
                        {"title": "川剧绝活：变脸·吐火·钻火圈", "url": "https://search.bilibili.com/all?keyword=川剧+变脸+吐火+钻火圈", "type": "video", "desc": "目不暇接的四川戏曲绝技"},
                        {"title": "黄梅戏进校园：非遗传承从娃娃抓起", "url": "https://search.bilibili.com/all?keyword=黄梅戏+进校园+非遗传承", "type": "video", "desc": "感人的传承故事，守护文化根脉"},
                    ], ensure_ascii=False),
                    published_at=datetime(2026, 3, 17),
                    is_published=True,
                ),
            ]
            for dd in digests_data:
                db.add(WeeklyDigest(**dd))
            db.commit()
            print(f"已插入 {len(digests_data)} 期每周荐读")
        else:
            print(f"每周荐读表已有 {digest_count} 条数据，跳过")

        print("\n种子数据插入完成！")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
