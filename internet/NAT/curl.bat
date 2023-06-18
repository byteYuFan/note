@echo off
setlocal

set url=pogf.com.cn:60000  // 替换为你要请求的网站地址
set iterations=10  // 指定要执行的迭代次数

for /l %%i in (1,1,%iterations%) do (
    curl %url%
    echo.
)

endlocal
