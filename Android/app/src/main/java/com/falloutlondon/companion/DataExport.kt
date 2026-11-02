package com.falloutlondon.companion

fun PipboyValue.displayText(): String = when (this) {
    is PipboyValue.Bool -> value.toString()
    is PipboyValue.Int8 -> value.toString()
    is PipboyValue.UInt8 -> value.toString()
    is PipboyValue.Int32 -> value.toString()
    is PipboyValue.UInt32 -> value.toString()
    is PipboyValue.Float32 -> value.toString()
    is PipboyValue.StringValue -> value.replace("\n", "\\n").replace("\r", "\\r")
    PipboyValue.Null -> "null"
}

fun PipboyDatabase.exportText(gameWorld: String, dataSource: String): String {
    val out = StringBuilder()
    out.appendLine("ATTA-BOY DIAGNOSTIC DATA EXPORT")
    out.appendLine("Game world: $gameWorld")
    out.appendLine("Data source: $dataSource")
    out.appendLine("Generated UTC epoch ms: ${System.currentTimeMillis()}")
    out.appendLine("Database nodes: ${nodes.size}")
    out.appendLine("Decoded value paths: ${flattenedValues().size}")
    out.appendLine("Review before sharing: player, inventory, quest and save-specific data may be present.")
    out.appendLine()
    out.appendLine("DECODED DATABASE TREE")
    out.appendLine("=====================")

    val visited = mutableSetOf<Long>()
    fun walk(id: Long, path: String, depth: Int) {
        val node = nodes[id] ?: return
        val indent = "  ".repeat(depth)
        val type = when (val value = node.value) {
            is PipboyValue.Bool -> "Bool"
            is PipboyValue.Int8 -> "Int8"
            is PipboyValue.UInt8 -> "UInt8"
            is PipboyValue.Int32 -> "Int32"
            is PipboyValue.UInt32 -> "UInt32"
            is PipboyValue.Float32 -> "Float32"
            is PipboyValue.StringValue -> "String"
            PipboyValue.Null -> "Null"
            null -> when {
                node.arrayChildren.isNotEmpty() -> "Array"
                node.objectChildren.isNotEmpty() -> "Object"
                else -> "Empty"
            }
        }
        val label = path.ifEmpty { "ROOT" }
        val value = node.value?.displayText()?.let { " = $it" }.orEmpty()
        out.append(indent).append(label)
            .append(" [node=").append(id)
            .append(", type=").append(type)
            .append(", objectChildren=").append(node.objectChildren.size)
            .append(", arrayChildren=").append(node.arrayChildren.size)
            .append("]").append(value).appendLine()

        if (!visited.add(id)) {
            out.append(indent).append("  [already visited node; traversal stopped]").appendLine()
            return
        }
        node.objectChildren.toSortedMap().forEach { (key, child) ->
            walk(child, if (path.isEmpty()) key else "$path.$key", depth + 1)
        }
        node.arrayChildren.forEachIndexed { index, child ->
            walk(child, if (path.isEmpty()) "[$index]" else "$path[$index]", depth + 1)
        }
    }

    walk(0L, "", 0)
    localMap?.let {
        out.appendLine()
        out.appendLine("LOCAL MAP SNAPSHOT")
        out.appendLine("  size = ${it.width} x ${it.height}")
        out.appendLine("  northWest = ${it.northWest}")
        out.appendLine("  northEast = ${it.northEast}")
        out.appendLine("  southWest = ${it.southWest}")
        out.appendLine("  pixels = ${it.pixels.size} bytes")
    }
    out.appendLine()
    out.appendLine("END OF EXPORT")
    return out.toString()
}
