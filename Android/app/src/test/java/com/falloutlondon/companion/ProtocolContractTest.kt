package com.falloutlondon.companion

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ProtocolContractTest {
    @Test fun decodesLittleEndianBooleanRecord() {
        val payload = byteArrayOf(0) + u32(0x12345678L) + byteArrayOf(1)
        assertEquals(
            PipboyUpdate.Data(listOf(PipboyRecord.Value(0x12345678L, PipboyValue.Bool(true)))),
            PipboyPacketDecoder.decode(3, payload)
        )
    }

    @Test fun decodesCommandResponseAsUtf8() {
        assertEquals(
            PipboyUpdate.CommandResponse("""{"ok":true}"""),
            PipboyPacketDecoder.decode(6, """{"ok":true}""".toByteArray())
        )
    }

    @Test fun preservesUnknownMessageTypes() {
        val payload = byteArrayOf(4, 5, 6)
        val decoded = PipboyPacketDecoder.decode(99, payload)
        assertTrue(decoded is PipboyUpdate.Unknown)
        assertEquals(99, (decoded as PipboyUpdate.Unknown).type)
        assertTrue(payload.contentEquals(decoded.payload))
    }

    @Test fun rejectsTruncatedLocalMapHeader() {
        assertNull(PipboyPacketDecoder.decode(4, byteArrayOf(1, 2, 3)))
    }

    @Test fun appliesIncrementalObjectGraphUpdatesToPaths() {
        val database = PipboyDatabase()
        database.apply(PipboyUpdate.Data(listOf(
            PipboyRecord.Object(0L, listOf("playerinfo" to 10L), emptyList()),
            PipboyRecord.Object(10L, listOf("currhp" to 11L), emptyList()),
            PipboyRecord.Value(11L, PipboyValue.Float32(87.5f))
        )))
        assertEquals(PipboyValue.Float32(87.5f), database.value("playerinfo.currhp"))
    }

    private fun u32(value: Long) = byteArrayOf(
        value.toByte(), (value shr 8).toByte(), (value shr 16).toByte(), (value shr 24).toByte()
    )
}
