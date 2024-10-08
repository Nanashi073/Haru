




---
title: " 差生文具多｜关于RSS"
date: 2024-06-28T11:49:27+08:00
lastmod: 2024-06-28T11:49:27+08:00
description: click to read more
tags:
- 差生文具多
categories:
- others
image: 
slug: other-about-rss
---




## 为什么RSS

因为吃太饱了（即答）。

其实主要是为了抑制我对sns的渴望，有了RSS之后，确实有效降低了我打开各大APP当互联网街溜子的频率，而且帮我优化掉了知乎、少数派和机核网的APP，或许过一阵子可以把油管也优化掉了。

最开始用RSS，就是因为看见了少数派上的[一篇文章](https://sspai.com/post/56198)。后来又看见了[椒盐豆豉的这篇文章](https://blog.douchi.space/my-rss-setup/)，给我增加了一些很好的订阅源，同时也删掉了一些。最近看见了[这篇博文](https://gregueria.icu/posts/all-about-rss/)，学会了怎么用RSS订阅Lofter（虽然我已经戒了），主要是仔细看了一下[RSShub](https://docs.rsshub.app/zh/)的文档，发现了很多好东西，于是写了这篇博客。

## 用什么看RSS

我一直用的都是Reeder5（苹果全家桶限定），货比三家之后，这个真是最优解，老牌，订阅制，维护者一直活着没跑，页面特别好看（用码男最爱的词：优雅）。而且还有Read it Later，有Safari快捷键可以一键保存，也可以方便的把RSS里的文章一键保存。我不是这种功能的重度用户，所以Reeder的Read it Later完全够用。我只拿这个功能来存需要放进博客链接的文章，有什么想看的都直接看了，毕竟堆进稍后读的结局一般都是从不读。

但是Reeder唯一的缺点就是……抓取的太慢了！必须要翻墙，而且必须要特定的节点才能抓取，至少我这个梯子是这样。为此我琢磨了半天，最终发现一件事：Reeder和其他自定义度高的RSS阅读器一样，可以添加其他乱七八糟的玩意的账户，比如Inoreader，Feedly，往下拉有Self-Host选项，里面有一个叫FreshRSS的东西。

于是我飞快地上了VPS，打开文档，拉取镜像，import OPML一气呵成。不搞子域名了，麻烦。在Reeder里添加FreshRSS账户后，也发现了一个缺点：有些源抓不到。我研究了一下，觉得是有一阵子没更新的就抓不到，而且一些B站的源，能不能抓到要看缘分。不过无所谓，这个更新起来真的飞快，还不需要翻墙，搭配Reeder就很完美，不需要再折腾了。

## RSS优质好源

推荐一些我喜欢的RSS源，内含一些对各大平台的抱怨恶口。一些大家都在定的什么小众软件啊，NPR全家桶就不列上了。
### 小宇宙我恨你

隐隐感觉之前就看见，有人辱骂小宇宙越做越封闭，死抱着RSS不撒手。有些小宇宙的源偶尔能从pocket cast上找到，但自从我换了Castro，靠搜索发现中文播客就成了不可能的任务。好在RSS HUB能轻松地分发小宇宙的RSS，

目前我倒过来的博客有：蓝色漂浮；永远年轻音乐磁带；落日之后；负一楼；异地登陆；脑髓地狱。
### B站我恨你

我关注了很多那种……美学博主。其实本质就是搬运一些国外摄影师和画家艺术家的美图，做成视频或者发图包，去油管搜了一圈果然没有平替。这些东西我是需要在电脑端打开的，幸好RSSHUB的插件能一键直接找到UP主的RSS，还算方便。FreshRSS过了好几天，到现在才能抓取到B站的源。我也不知道为什么，能用就行。

我订阅的有：冯墨风；可可酱jz；美学集；长期洗涤Longwashing；画画的春哥；Rofix；裸子植物；小王同学喜欢富士；小盆友photo；写真部；移觉社；音乐影画；MuFo美物记；摄影审美积累；色彩的美学；匆匆誌

反正B站一搜都能找到，我就不费劲吧啦地附上超链接了。

### 杂七杂八

[Modern Mrs Darcy](https://modernmrsdarcy.com/)：我是从听播客开始的知道这个博主的，然后发现原来还有一个博客（当然也有油管，不过我不看）。播客很好听，声音催眠，博客会放一些reading list和卖书和book club的广告，还有博客的transcript。每周有一个Links I Love的保留节目，内容类似于我的阅读报告里的互联网街溜子（…），只有这个我每期都看。

[Everand blog](https://www.everand.com/blog)：Everand一个类似微信读书的网站，不过内容是纯订阅制，花了钱才能看，里面不仅有书还有播客和有声书，亚马逊kindle商店升级版，当然库显然没亚马逊全。他们的blog会定期推一些书单，我每次只看thriller/crime相关的。

说起来goodread的blog也会推书单，但是他们的书单往往长得恐怖，而且可能是因为放的全是goodread链接，抓过来的阅读器界面里，图书栏都显示一串数字id，必须点进源网站查看，很烦。

[上海书评](https://pullopen.xyz/@shuping/112687302960116939)：澎湃的上海书评的毛象镜像。有空我应该把链接换成原本的，感觉也能抓，就是麻烦一点。

[The Paris Review](https://www.theparisreview.org/)：大家应该都知道这是啥吧！一些深度好文。经常因为太深度也太长了懒得看完，偶尔会有感兴趣的。

[Fiction University](http://blog.janicehardy.com/)：一些实用的虚构写作小技巧，就我看下来，感觉都很无门槛，给非科班0基础的人准备的写作小撇步。

其实我不知道撇步到底是什么意思，但是感觉很时髦一词，就随便用一下。



