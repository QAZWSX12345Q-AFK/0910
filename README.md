# 基金定投助手

这是一个以开源投资追踪项目的思路为底座、针对中国基金定投重新设计的 MVP。

参考项目：
- piginzoo/fund_analysis：基金历史数据、定投分析、真实投资计划和利润计算
- mike840609/assets_tracker（astt）：Next.js/PWA、投资组合、定期投资、每日快照、自托管
- MisterStranger03/Investfolio：基金/投资组合、XIRR、移动端 PWA

## 当前 MVP

- 手机/桌面响应式 Dashboard
- 新增每日/每周/每月定投计划
- 本地保存定投计划
- 基础累计投入、估值、收益和收益率计算
- 基金 API Provider 独立接口
- PWA manifest
- 为后续真实净值、交易流水、XIRR、云数据库预留结构

> 当前演示使用临时净值计算，不应作为真实投资收益依据。

## 本地运行

需要 Node.js 20+：

```bash
npm install
npm run dev
```

浏览器打开：

http://localhost:3000

## 下一阶段

1. 接入稳定的中国基金历史/实时净值 Provider
2. 建立 PostgreSQL + Prisma 数据库
3. 将每笔定投保存为 transaction/lot
4. 按实际净值计算份额和滚存收益
5. 加入 XIRR、每日收益、月度收益、年度收益
6. 增加登录和云端同步
7. 配置 GitHub Actions 定时更新净值
8. Vercel + PostgreSQL 部署
9. PWA 安装与移动端优化

## GitHub

建议新建私有仓库，例如：

fund-dca-app

然后：

```bash
git init
git add .
git commit -m "feat: initial fund DCA tracker"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/fund-dca-app.git
git push -u origin main
```

## License

本项目自己的新增代码可按 MIT 使用。被参考的第三方项目仍需遵守各自 LICENSE。发布前请核对依赖和原项目许可证。