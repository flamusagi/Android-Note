package com.example.administrator.note;

import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.ContextMenu;
import android.view.KeyEvent;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private ListView listView;
    private FloatingActionButton buttonAdd;
    private FloatingActionButton buttonExit,buttonSync;
    private NoteAdapter adapter;
    private Intent intent;
    private NoteHelper noteHelper;
    private SQLiteDatabase database;
    private long mExitTime;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initView();
        initFab();
    }

    @Override
    protected void onResume() {
        super.onResume();
        queryAll();
    }

    private void initView(){
        listView = findViewById(R.id.list_view);
        registerForContextMenu(listView);

        noteHelper = new NoteHelper(this);
        database = noteHelper.getReadableDatabase();
    }

    private void initFab(){
        buttonAdd = findViewById(R.id.fab_add);
        buttonAdd.setOnClickListener(this);
        buttonExit = findViewById(R.id.fab_exit);
        buttonExit.setOnClickListener(this);
        buttonSync = findViewById(R.id.fab_sync);
        buttonSync.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch(v.getId()){
            case R.id.fab_add:
                intent = new Intent(MainActivity.this, ActionActivity.class);
                intent.putExtra("action", 1);
                startActivity(intent);
                break;
            case R.id.fab_exit:
                System.exit(0);
                break;
            case R.id.fab_sync:
                intent = new Intent(MainActivity.this, CloudActivity.class);
                System.out.println(intent);

                startActivity(intent);
                break;
            default:
                break;
        }

    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        //判断用户是否点击了“返回键”
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            //与上次点击返回键时刻作差
            if ((System.currentTimeMillis() - mExitTime) > 2000) {
                //大于2000ms则认为是误操作，使用Toast进行提示
                Toast.makeText(this, "再按一次退出程序", Toast.LENGTH_SHORT).show();
                //并记录下本次点击“返回键”的时刻，以便下次进行判断
                mExitTime = System.currentTimeMillis();
            } else {
                //小于2000ms则认为是用户确实希望退出程序-调用System.exit()方法进行退出
                System.exit(0);
            }
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    /**
     * 长按弹出删除菜单
     * @param menu
     * @param v
     * @param menuInfo
     */
    @Override
    public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo) {
        super.onCreateContextMenu(menu, v, menuInfo);
        getMenuInflater().inflate(R.menu.context_menu, menu); // Create a menu from an XML resource
    }

    @Override
    public boolean onContextItemSelected(MenuItem item) {
        AdapterView.AdapterContextMenuInfo info = (AdapterView.AdapterContextMenuInfo) item.getMenuInfo();
        int position = info.position;

        Cursor cursor = database.query(noteHelper.tableName, null,null,null,null,null, noteHelper.id);
        cursor.moveToPosition(position);
        int noteId = cursor.getInt(cursor.getColumnIndexOrThrow(NoteHelper.id));

        switch (item.getItemId()) {
            case R.id.menu_delete:
                // Delete the selected note
                deleteNote(noteId);
                return true;
            default:
                return super.onContextItemSelected(item);
        }
    }

    /**
     * 占位符 防止sql注入
     * @param noteId
     */
    private void deleteNote(int noteId) {
        // Delete the note with the given ID from the database
        String selection = NoteHelper.id + " = ?";
        String[] selectionArgs = {String.valueOf(noteId)};
        database.delete(NoteHelper.tableName, selection, selectionArgs);

        // Update the ListView to reflect the changes
        queryAll();

        // Optionally, you can show a toast to confirm the deletion
        Toast.makeText(this, "Note deleted", Toast.LENGTH_SHORT).show();
    }

    /**
     * 展示列表的备忘录数据
     */
    public void queryAll(){
        Cursor cursor = database.query(NoteHelper.tableName, null,null,null,null,null, noteHelper.lastModifyTime);
        adapter = new NoteAdapter(this, cursor);
        listView.setAdapter(adapter);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent intent = new Intent(MainActivity.this, LookNoteActivity.class);
                intent.putExtra("i", position);
                /**
                 * 首先执行sql语句返回查询结果给cursor，然后通过position可以知道数据的具体行数，再使用getColumnIndex直接找出所对应列的具体数据。
                 */
                Cursor cursor = database.query(noteHelper.tableName, null,null,null,null,null, noteHelper.id);
                cursor.moveToPosition(position);
                String[] keysToInclude = {
                        noteHelper.id,
                        noteHelper.content,
                        noteHelper.lastModifyTime,
                        noteHelper.title
                };
                for (String key : keysToInclude) {
                    int columnIndex = cursor.getColumnIndex(key);
                    if (columnIndex != -1) {
                        intent.putExtra(key, cursor.getString(columnIndex));
                    }
                }

                startActivity(intent);
            }
        });
    }
}
