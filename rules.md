# firecrawl2md
在当前目录有一个input.txt文件，以及一个output文件夹。
input.txt文件内每一行都是一个网页的url，现在，你需要实现如下的功能：
1. 遍历input.txt中的每一行，使用firecrawl爬取每一行对应的网页，并将主要内容（不包含导航栏）保存为markdown文件存入output文件夹内
2. 调用llm分块修复每一个markdown文件，修复的markdown文件替代原有markdown文件即可，分块逻辑如下：
首先定义一个最大token数，比如32k，然后每个分块都是以#/##/###/####开头的，结尾一定是#/##/###/####的上一行，每个分块都尽可能接近最大token数，但是不能超过最大token数。（也就是说，每个分块都是动态的）

修复要点如下：
(1). 确保层级关系准确，比如#/##/###/####的层级关系是正确的
(2). 确保行内公式，变量都使用$ ... $包裹，行间公式变量使用$$ ... $$包裹
(3). 确保代码块使用```包裹，并且代码块的languages使用```languages包裹
(4). 确保表格使用|...|...|...|包裹，并且表格的列使用:-:包裹
(5). 确保图片使用![](...)包裹，并且图片的alt使用![alt](...)包裹
(6). 确保链接使用[](...)包裹，并且链接的title使用[title](...)包裹

3. 使用llm根据markdown内容生成文件名，文件名只能由英文，下划线构成，然后重命名markdown文件
4. 遍历每个markdown文件，遍历每个markdown文件内的图片链接，执行如下操作：
(1). 先在output/images文件夹内创建以markdown文件名命名的文件夹，
(2). 然后依次下载该markdown文件中的图片到该文件夹，按照顺序命名为index.jpg，其中index从1开始，
(3). 然后将图片链接替换为图片的相对路径


注意事项：
1. 确保模块之间是严格解耦的，便于复盘，理解每部分的功能
2. 所有的函数，类函数的输入，输出必须使用类型注解，并借助Annotated添加中文说明，示例如下：

```python
def mc_policy_evaluation(
    env: Annotated[GridWorldMC, "蒙特卡洛网格环境"],
    policy: Annotated[np.ndarray, "当前策略概率矩阵"],
    Q: Annotated[np.ndarray, "状态-动作价值表"],
    gamma: Annotated[float, "折扣因子"],
    num_episodes: Annotated[int, "每个(s,a)采样的回合数"],
) -> Annotated[np.ndarray, "更新后的状态-动作价值表"]:
    pass
```
3. 每个函数都要在开头使用"""..."""添加功能说明，确保函数的调用者能够理解该函数的功能。
4. llm使用deepseek，deepseek的api_key， friecrawl的api_key全部存放在.env文件内，使用dotenv的loadenv()函数加载
5. 你在生成整个项目的过程中禁止生成任何md文件，你只能将内容更新到README.md文件中
6. 整个项目使用uv包管理器，你需要安装好uv环境，并将相关依赖存入requirements.txt文件内