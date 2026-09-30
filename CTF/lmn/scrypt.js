/**
 * scrypt cho trình duyệt — bản dùng chung với `src/crypto/scrypt.js`.
 *
 * File này CỐ Ý là bản sao gần như nguyên văn của lõi ở server, chứ không phải một
 * bản cài đặt thứ hai. Lý do: bản ở server được kiểm chứng từng tham số với
 * `crypto.scryptSync` native của Node (test/scrypt.test.js). Giữ nguyên lõi nghĩa là
 * bảo chứng đó áp dụng luôn cho phía trình duyệt.
 *
 * Khác biệt duy nhất: PBKDF2 ở đây dùng WebCrypto (bất đồng bộ) thay vì
 * crypto.pbkdf2Sync. Lõi tính toán không đổi một dòng nào.
 *
 * Khi có bước build thật, file này nên được SINH RA từ src/crypto/scrypt.js chứ
 * không chép tay — chép tay là cách để hai bản trôi xa nhau theo thời gian.
 */

const R = (a, b) => (a << b) | (a >>> (32 - b));

function salsa20_8(B) {
  const x = new Uint32Array(16);
  x.set(B);
  for (let i = 0; i < 8; i += 2) {
    x[4] ^= R(x[0] + x[12], 7); x[8] ^= R(x[4] + x[0], 9);
    x[12] ^= R(x[8] + x[4], 13); x[0] ^= R(x[12] + x[8], 18);
    x[9] ^= R(x[5] + x[1], 7); x[13] ^= R(x[9] + x[5], 9);
    x[1] ^= R(x[13] + x[9], 13); x[5] ^= R(x[1] + x[13], 18);
    x[14] ^= R(x[10] + x[6], 7); x[2] ^= R(x[14] + x[10], 9);
    x[6] ^= R(x[2] + x[14], 13); x[10] ^= R(x[6] + x[2], 18);
    x[3] ^= R(x[15] + x[11], 7); x[7] ^= R(x[3] + x[15], 9);
    x[11] ^= R(x[7] + x[3], 13); x[15] ^= R(x[11] + x[7], 18);
    x[1] ^= R(x[0] + x[3], 7); x[2] ^= R(x[1] + x[0], 9);
    x[3] ^= R(x[2] + x[1], 13); x[0] ^= R(x[3] + x[2], 18);
    x[6] ^= R(x[5] + x[4], 7); x[7] ^= R(x[6] + x[5], 9);
    x[4] ^= R(x[7] + x[6], 13); x[5] ^= R(x[4] + x[7], 18);
    x[11] ^= R(x[10] + x[9], 7); x[8] ^= R(x[11] + x[10], 9);
    x[9] ^= R(x[8] + x[11], 13); x[10] ^= R(x[9] + x[8], 18);
    x[12] ^= R(x[15] + x[14], 7); x[13] ^= R(x[12] + x[15], 9);
    x[14] ^= R(x[13] + x[12], 13); x[15] ^= R(x[14] + x[13], 18);
  }
  for (let i = 0; i < 16; i++) B[i] = (B[i] + x[i]) >>> 0;
}

function blockMix(B, Y, r) {
  const X = new Uint32Array(16);
  X.set(B.subarray((2 * r - 1) * 16, 2 * r * 16));
  for (let i = 0; i < 2 * r; i++) {
    for (let j = 0; j < 16; j++) X[j] ^= B[i * 16 + j];
    salsa20_8(X);
    Y.set(X, (i % 2 === 0 ? i / 2 : r + (i - 1) / 2) * 16);
  }
}

function romix(B, N, r) {
  const len = 32 * r;
  const V = new Uint32Array(len * N);
  const X = new Uint32Array(B);
  const Y = new Uint32Array(len);
  for (let i = 0; i < N; i++) {
    V.set(X, i * len);
    blockMix(X, Y, r);
    X.set(Y);
  }
  for (let i = 0; i < N; i++) {
    const j = X[(2 * r - 1) * 16] & (N - 1);
    for (let k = 0; k < len; k++) X[k] ^= V[j * len + k];
    blockMix(X, Y, r);
    X.set(Y);
  }
  B.set(X);
}

function bufToU32(buf) {
  const out = new Uint32Array(buf.length / 4);
  for (let i = 0; i < out.length; i++) {
    out[i] = buf[i * 4] | (buf[i * 4 + 1] << 8) | (buf[i * 4 + 2] << 16) | (buf[i * 4 + 3] << 24);
  }
  return out;
}

function u32ToBuf(arr) {
  const out = new Uint8Array(arr.length * 4);
  const dv = new DataView(out.buffer);
  for (let i = 0; i < arr.length; i++) dv.setUint32(i * 4, arr[i] >>> 0, true);
  return out;
}

/** PBKDF2-HMAC-SHA256 qua WebCrypto. */
async function pbkdf2(password, salt, iterations, keylen) {
  const key = await crypto.subtle.importKey('raw', password, 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', hash: 'SHA-256', salt, iterations }, key, keylen * 8,
  );
  return new Uint8Array(bits);
}

export async function scrypt(password, salt, { N = 1024, r = 8, p = 1, dkLen = 32 } = {}) {
  if (N < 2 || (N & (N - 1)) !== 0) throw new Error('scrypt: N phải là luỹ thừa của 2');
  const B = await pbkdf2(password, salt, 1, p * 128 * r);
  const words = bufToU32(B);
  const len = 32 * r;
  for (let i = 0; i < p; i++) romix(words.subarray(i * len, (i + 1) * len), N, r);
  return pbkdf2(password, u32ToBuf(words), 1, dkLen);
}
