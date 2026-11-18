

---
title: "博客装修02｜搬家！！"
date: 2024-06-01T23:30:09+08:00
lastmod: 2024-06-01T23:30:09+08:00
description: 新主题上线！
tags:
- 差生文具多
- 装潢一条龙
categories:
- others
image: 
slug: 2024-others-blog-02
aliases:
  - /post/2024/other/other-07/2024-others-blog-02/
---




不由得想到，装修博客-写关于装修博客的博客，真是一个莫比乌斯环……
换了新主题，因为装修改了很多，所以写个博客记一下。

## 换主题

看了很多主题，包括BlowFish，mainroad（宝宝说这个像新闻网站），Book，LoveIt，Flat，Texify3。因为现在用的stack感觉太萌了（…）不适合我，想选一个更极简的。

看来看去选中了Diary。主要是因为移动端适配做得好，有侧边栏toc，移动端可以在旁边呼出菜单。我也没搬出hugo，短代码拾掇拾掇想必都能继续用吧！实在不行问ChatGPT。抱着这种心情，我先试着按教程那样直接切换主题，果然不行。我原本用的是塔塔的魔改版stack，很多代码直接改在了hugo本地文件，和新主题不兼容的地方有亿点多。

下面记录一下流程，以防万一将来我又要换主题但是忘记怎么搞了……顺便我是Mac。

```
hugo new site # 这里加上名字
cd # 这里后面加上文件夹的名字
init git
# 这一行是git安装教程的命令，主题的仓库里一般都有能拿来ctrlc的
echo “theme = ‘主题名字’” >> hugo.toml
```
这个是hugo官方文档里的说明。不过我发现，一般大家的那个文件都是叫`config.toml`。不过不要紧，总之是一个东西。

*update:有事，不改称config，vercel就不认，会构建网站失败。*

这个时候主题就安装上了，可以`hugo server`进去查看主题，并且根据主题的教程进行一些简单的自定义。

## 官方文档

Diary用的人比较少，文档也…不是那么全，里面写明的自定义部分就那么多。总之我先根据这里面的说明走了一遍，再查缺补漏。
### 更改配色

在`theme/diary/assets/scss/journal.scss`里第一行。
```$color-accent: #1976d2;```
这里改的是整体的配色，包括toc。下面两行可以改背景颜色。

但是因为toc的配色是一键更改的，我不太喜欢。在`journal.scss`里搜索toc，把字体大小放大了一点，固定了宽度，把背景颜色改了。方法是在这个地方`background: rgba($color-accent, 0.005);` 加了俩0。

###  自定义界面

官方文档是说在`config/toml`里面加，不过我发现，在`post/page`里面把我之前的页面复制粘贴过来，也有一样的效果。于是就这样了。调整了一下，把about页面和now页面合并了（……），RSS和象的链接也放进了about界面。
### 友链界面

原本的JSON不好使了，搞不明白，抄了谷歌来的作业。改成了用短代码和markdown来实现，简单清爽了很多。[链接在这里🔗](https://arc.net/l/quote/jldysrtr)。我重新设置了一下字体和颜色。

在我转移友链的时候，我突然发现哪里不对……我的图床链接怎么是我的ip啊？？在设置里找了半天，发现是储存路径没改。设置一下之后就好了，换成了我的子域名打头。

## 自定义部分
### 修改全站字体

我在这个上面折腾了好久！！然后才发现呃……是这样的。先在`themes/diary/layouts/partials/extended_head.html`里，加入这个：
```
<style>

  :root {

    --sys-font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Droid Sans", "Helvetica Neue";

    --zh-font-family: "Noto Serif SC", "Hiragino Sans GB", "Droid Sans Fallback", "Microsoft YaHei";

    --base-font-family: "Noto Serif SC", var(--sys-font-family), var(--zh-font-family), sans-serif;

    --code-font-family: Menlo, Monaco, Consolas, "Courier New", monospace;

}

</style>
<script>  // 正文自重300，标题字重700

        (function () {

            const customFont = document.createElement('link');

            customFont.href = "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap";

            customFont.type = "text/css";

            customFont.rel = "stylesheet";

            document.head.appendChild(customFont);

        }());

</script>
```
然后再到`journal.scss`里，紧挨着颜色下面就是字体设置，在前面挨个加入‘Noto Serif SC'，然后再往下翻，有一串长这个样子的代码，把里面的字体也换下名字就好了。
```
body {

  background: $back-container-background;

  padding: 0;

  margin: 0;

  font-family: Noto Serif SC;

  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.004);

  text-rendering: optimizeLegibility !important;

  -webkit-font-smoothing: antialiased !important;

  color: $color-text;

}
```

### 标题样式

代码是ChatGPT给的，复制粘贴到h1h2h3的字体大小那一串的代码下面。
```
body, p, div, span {

  font-family: $default-font-list;

}

  

h1, h2, h3, h4, h5 {

  font-family: 'Noto Serif SC', sans-serif; // 使用黑体

  color: #4c0000; // 使用不同颜色

  position: relative;

  padding-left: 1.5em; // 给#符号预留空间

}

  

h1 {

  border-bottom: 2px solid #4c0000; // 下划线

  padding-bottom: 5px;

}

  

h2 {

  border-bottom: 2px solid #4c0000; // 下划线

  padding-bottom: 5px;

}

  

  

h1::before, h2::before, h3::before, h4::before, h5::before {

  position: absolute;

  left: -1.5em; // 调整符号位置

  color: #4c0000; // 符号的颜色

  font-weight: bold; // 符号的加粗

}

  

h1::before {

  content: '#';

}

  

h2::before {

  content: '##';

}

  

h3::before {

  content: '###';

}

  

h4::before {

  content: '####';

}

  

h5::before {

  content: '#####';

}

```

### 超链接样式

改来改去最后就加了个下划线，代码来自ChatGPT。

```
/* 为所有链接添加样式 */

a {

color: #7e0808; /* 链接颜色 */

text-decoration: underline; /* 去掉下划线 */

}

  

a:hover {

color: #a30f07; /* 悬停时的颜色 */

text-decoration: underline; /* 悬停时的下划线 */

}

  

/* 为特定类名的链接添加样式 */

.custom-link {

color: #ff5722;

font-weight: bold;

}
```

### 自定义footer

在左下角加入了“博客已运行多久多久”和“写了多少篇文章·多少字”，用的是香油[第三夏尔的这一篇教程](https://thirdshire.com/hugo-stack-renovation/)。不过我的主题比较格路，所以我是在copyright下面加的这两行字……SCSS是放在了主题的SCSS里。以及大家应该都知道了（我才知道）`hasCJKLanguage = true`要放到`config.toml`的最上面。

以及，字数统计用的是[椒盐豆豉的教程](https://blog.douchi.space/blog-decoration/#gsc.tab=0)。

## 短代码

### 进度条

特别鸣谢：ChatGPT。

在`/shotcodes/progressbar.html`里加入下面这些东西：
```
<div class="progress-bar-container">
  <div class="progress-bar" style="width: {{ .Get "percentage" }}%;">
    <span class="progress-text">{{ .Get "percentage" }}%</span>
  </div>
</div>
```

在scss文件里加入下面这些东西：
```
.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 25px;
  overflow: hidden;
  height: 20px;
  position: relative; /* 添加 position: relative; */
}

.progress-bar {
  height: 100%;
  background-color: #76c7c0; /* 你可以根据需要更改颜色 */
  border-radius: 25px 0 0 25px;
  position: relative; /* 添加 position: relative; */
}

.progress-text {
  position: absolute; /* 使用绝对定位 */
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  color: white; /* 文字颜色 */
  font-weight: bold; /* 字体加粗 */
  line-height: 20px; /* 确保文字垂直居中 */
}
```

用的时候这样用：
```
{< progressbar percentage="75" >} // 换双括号！
```
### 星星评分

再次感谢……嗯。还是ChatGPT。

新建`star_rating.html`短代码：
```
<div class="star-rating">
  {{ $rating := .Get "rating" }}
  {{ range seq 1 5 }}
    {{ if le . $rating }}
      <span class="star filled">★</span>
    {{ else }}
      <span class="star">☆</span>
    {{ end }}
  {{ end }}
</div>
```

CSS:
```
.star-rating {
  display: inline-block;
}

.star {
  font-size: 24px; /* 根据需要调整星星大小 */
  color: #ccc; /* 未填充星星的颜色 */
}

.star.filled {
  color: #f5a623; /* 填充星星的颜色 */
}
```

使用时加双括号：
```
{< star_rating rating="7" >}
```
## 没搞明白的

- 看到了[一篇教程](https://blog.loikein.one/posts/2022-08-11-hugo-copy-code-button/)，说怎么给代码块增加copy按钮。这个教程和我用的是一个主题，然而我照抄了之后不好使……算了，不碍事！先放着吧！
- 想开启三栏然后把tag云和搜索框什么的放到右边，但是好麻烦，而且现在这样也挺好看的。放置。
- 和博客没关系，但是想把dashboard换成[flare](https://immmmm.com/startpage-flare/)，因为听说更快。
- [单向历](https://immmmm.com/dan-xiang-li-page/)，想要但是感觉链接是不是挂了？
- twikoo评论，下次再说吧……