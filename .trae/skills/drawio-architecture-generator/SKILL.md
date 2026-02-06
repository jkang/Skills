---
name: drawio-architecture-generator
description: 基于应用架构描述文本，自动生成可导入到 draw.io 的 XML（mxfile/mxGraphModel）。当用户提供架构分层、组件与连接关系，并要求输出 draw.io 图时使用。
---

# Draw.io 架构图生成

## 快速用法
- 输入：自然语言的应用架构描述（分层、组件、关系）
- 输出：可直接导入 draw.io 的 XML（支持 mxfile 包裹或仅 mxGraphModel）
- 导入：在 draw.io 中选择 File > Import from > Device，将生成的 XML 导入

## 输出结构
- 顶层使用 mxfile/diagram 包裹，内部包含 mxGraphModel
- mxGraphModel/root 中至少包含两个初始单元
  - mxCell id="0"
  - mxCell id="1" parent="0"
- 图元
  - 顶层或容器：vertex="1"，parent 指向所在层（通常为 1 或容器 id）
  - 边：edge="1"，source/target 指向对应组件 id
- 几何
  - 顶层容器：mxGeometry x/y/width/height
  - 子组件：mxGeometry 相对容器坐标的 x/y/width/height

## 元素与样式
- 层容器：style="rounded=1;whiteSpace=wrap;html=1;container=1;align=center;verticalAlign=top;strokeColor=#B3B3B3;fillColor=#F5F5F5"
- 普通组件：style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF"
- 数据存储：style="shape=cylinder;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF"
- 边：style="endArrow=classic;html=1"（可选 dashed=1）

## 布局与坐标
- 分层自上而下排列，层间垂直间距 120
- 容器宽度统一，例如 1100；左右外边距 20
- 组件在容器内水平放置，组件之间水平间距 160，垂直居中（y≈60 或 40）
- 需要跨层连线时，边的 parent=1，mxGeometry relative="1"

## 输入解析规则
- 层：识别关键词如 Client、API Gateway、Application Services、Domain、Data、Infrastructure 等
- 组件：每层中提取以名词短语表示的单元（如 “User Service”）
- 关系：
  - “A -> B” 表示从 A 指向 B 的边
  - 支持跨层关系（如 Service -> Database）
- 标签文本直接写入 mxCell 的 value 属性（支持 html=1）

## 生成步骤
1. 解析文本为层、组件、关系三类结构化数据
2. 为 root 生成初始 mxCell id=0 与 id=1
3. 按层序生成容器 mxCell，计算几何坐标
4. 在容器内生成组件 mxCell，计算相对坐标
5. 为每条关系生成 edge mxCell，设置 source/target
6. 输出 mxfile/diagram/mxGraphModel 包裹的完整 XML

## 示例输出（可导入）

```xml
<mxfile host="app.diagrams.net" modified="2026-02-03T00:00:00.000Z" agent="drawio-architecture-generator" version="15.8.7" type="device">
  <diagram id="layered-arch" name="Layered Architecture">
    <mxGraphModel dx="1687" dy="681" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="L_client" value="Client" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#B3B3B3;fillColor=#F5F5F5;align=center;verticalAlign=top;container=1;" vertex="1" connectable="0" parent="1">
          <mxGeometry x="20" y="20" width="1100" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="C_web" value="Web App" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_client">
          <mxGeometry x="40" y="40" width="140" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="C_mobile" value="Mobile App" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_client">
          <mxGeometry x="220" y="40" width="140" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="L_gateway" value="API Gateway" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#B3B3B3;fillColor=#F5F5F5;align=center;verticalAlign=top;container=1;" vertex="1" connectable="0" parent="1">
          <mxGeometry x="20" y="160" width="1100" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="C_gateway" value="Gateway" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_gateway">
          <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="L_services" value="Application Services" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#B3B3B3;fillColor=#F5F5F5;align=center;verticalAlign=top;container=1;" vertex="1" connectable="0" parent="1">
          <mxGeometry x="20" y="300" width="1100" height="160" as="geometry"/>
        </mxCell>
        <mxCell id="C_user_service" value="User Service" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_services">
          <mxGeometry x="40" y="60" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="C_order_service" value="Order Service" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_services">
          <mxGeometry x="240" y="60" width="160" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="L_domain" value="Domain" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#B3B3B3;fillColor=#F5F5F5;align=center;verticalAlign=top;container=1;" vertex="1" connectable="0" parent="1">
          <mxGeometry x="20" y="480" width="1100" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="C_domain_model" value="Domain Model" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_domain">
          <mxGeometry x="40" y="40" width="180" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="L_data" value="Data &amp; Infra" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#B3B3B3;fillColor=#F5F5F5;align=center;verticalAlign=top;container=1;" vertex="1" connectable="0" parent="1">
          <mxGeometry x="20" y="620" width="1100" height="160" as="geometry"/>
        </mxCell>
        <mxCell id="C_db" value="Database" style="shape=cylinder;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_data">
          <mxGeometry x="40" y="60" width="120" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="C_broker" value="Message Broker" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#666666;fillColor=#FFFFFF;" vertex="1" parent="L_data">
          <mxGeometry x="200" y="70" width="160" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="E_web_gateway" value="" style="endArrow=classic;html=1;" edge="1" source="C_web" target="C_gateway" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_mobile_gateway" value="" style="endArrow=classic;html=1;" edge="1" source="C_mobile" target="C_gateway" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_gateway_user" value="" style="endArrow=classic;html=1;" edge="1" source="C_gateway" target="C_user_service" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_gateway_order" value="" style="endArrow=classic;html=1;" edge="1" source="C_gateway" target="C_order_service" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_user_domain" value="" style="endArrow=classic;html=1;" edge="1" source="C_user_service" target="C_domain_model" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_order_domain" value="" style="endArrow=classic;html=1;" edge="1" source="C_order_service" target="C_domain_model" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_domain_db" value="" style="endArrow=classic;html=1;" edge="1" source="C_domain_model" target="C_db" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="E_services_broker" value="" style="endArrow=classic;html=1;dashed=1;" edge="1" source="C_order_service" target="C_broker" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 校验与导入
- 在 draw.io 中使用 Extras > Edit Diagram 可查看 XML 源
- 如果遇到压缩 .drawio 内容，可参考官方解压说明以转换为未压缩 XML

## 参考
- jgraph 讨论与示例（mxGraphModel 基本结构）：https://github.com/jgraph/drawio/discussions/4170
- 官方文档：源编辑与格式说明：https://www.drawio.com/doc/faq/diagram-source-edit
- 自定义库文件格式（mxGraphModel 示例）：https://www.drawio.com/doc/faq/format-custom-shape-library
